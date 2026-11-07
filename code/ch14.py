"""第14章代码练习：主仪器—从仪器校准迁移与元数据检查。

任务对象
--------
同一批样品分别由主仪器与从仪器测量。主仪器上训练 NIR 定量模型，比较：
1. 从仪器光谱直接套用主仪器模型；
2. 输出斜率—偏差校正；
3. 全局直接标准化 DS；
4. 分段直接标准化 PDS。

独立目标域测试样品不参与训练或迁移函数拟合。所有数据由固定随机种子合成，
只用于保证代码可复现和说明方法边界，不代表真实仪器性能。
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
DATA = ROOT / "data"


@dataclass
class SpectralDataset:
    wavelengths: np.ndarray
    x_master: np.ndarray
    x_slave: np.ndarray
    y: np.ndarray
    sample_ids: list[str]


def _gaussian(x: np.ndarray, center: float, width: float, amplitude: float) -> np.ndarray:
    return amplitude * np.exp(-0.5 * ((x - center) / width) ** 2)


def _stratified_unit_samples(n: int, dimensions: int, rng: np.random.Generator) -> np.ndarray:
    """Latin-hypercube-like samples in [0, 1] for broad concentration coverage."""
    result = np.empty((n, dimensions), dtype=float)
    for dim in range(dimensions):
        strata = (np.arange(n) + rng.random(n)) / n
        result[:, dim] = rng.permutation(strata)
    return result


def generate_case(seed: int = 42) -> tuple[SpectralDataset, SpectralDataset, SpectralDataset, np.ndarray]:
    """Generate master training, transfer and independent target-domain sets."""
    rng = np.random.default_rng(seed)
    wavelengths = np.linspace(1100.0, 2400.0, 160)

    # Three chemically overlapping components. Component 0 is the target analyte.
    master_components = np.vstack(
        [
            _gaussian(wavelengths, 1450, 55, 1.0)
            + _gaussian(wavelengths, 1930, 72, 0.78)
            + _gaussian(wavelengths, 2200, 95, 0.36),
            _gaussian(wavelengths, 1510, 48, 0.72)
            + _gaussian(wavelengths, 2050, 80, 0.94)
            + _gaussian(wavelengths, 2320, 70, 0.25),
            _gaussian(wavelengths, 1680, 78, 0.62)
            + _gaussian(wavelengths, 2150, 68, 0.57)
            + _gaussian(wavelengths, 2380, 90, 0.34),
        ]
    )

    # The slave instrument has a wavelength shift/warp, detector gain and a
    # wavelength-dependent response. Traditional hardware calibration would
    # reduce these first; the remaining differences motivate DS/PDS.
    slave_wavelengths = wavelengths + 3.4 - 0.0012 * (wavelengths - 1750)
    slave_components = np.vstack(
        [
            np.interp(wavelengths, slave_wavelengths, component, left=0, right=0)
            for component in master_components
        ]
    )
    response = 0.82 + 0.16 * np.exp(-0.5 * ((wavelengths - 1950) / 420) ** 2)
    slave_components *= response

    def concentrations(n: int) -> np.ndarray:
        unit = _stratified_unit_samples(n, 3, rng)
        return 0.03 + 0.82 * unit

    def measure(components: np.ndarray, conc: np.ndarray, instrument: str) -> np.ndarray:
        spectra = conc @ components
        baseline = (
            0.015 * np.sin((wavelengths - 1100) / 360)
            + 0.006 * (wavelengths - 1750) / 650
        )
        if instrument == "master":
            spectra = spectra + baseline + rng.normal(0, 0.0022, spectra.shape)
        else:
            spectra = spectra + 1.85 * baseline + rng.normal(0, 0.0034, spectra.shape)
        return spectra.astype(np.float64)

    c_train = concentrations(140)
    c_transfer = concentrations(42)
    c_test = concentrations(70)

    # Make the independent test set deliberately include the high-concentration
    # region where extrapolation failures are easier to diagnose.
    c_test[:14, 0] = np.linspace(0.72, 0.92, 14)

    x_master_train = measure(master_components, c_train, "master")
    x_master_transfer = measure(master_components, c_transfer, "master")
    x_slave_transfer = measure(slave_components, c_transfer, "slave")
    x_slave_test = measure(slave_components, c_test, "slave")

    train = SpectralDataset(
        wavelengths,
        x_master_train,
        np.empty((0, wavelengths.size)),
        c_train[:, 0],
        [f"TR-{i:04d}" for i in range(1, len(c_train) + 1)],
    )
    transfer = SpectralDataset(
        wavelengths,
        x_master_transfer,
        x_slave_transfer,
        c_transfer[:, 0],
        [f"XT-{i:04d}" for i in range(1, len(c_transfer) + 1)],
    )
    test = SpectralDataset(
        wavelengths,
        np.empty((0, wavelengths.size)),
        x_slave_test,
        c_test[:, 0],
        [f"TS-{i:04d}" for i in range(1, len(c_test) + 1)],
    )
    return train, transfer, test, master_components


class PLS1:
    """Small dependency-free PLS-1 implementation for reproducible teaching."""

    def __init__(self, n_components: int = 9):
        self.n_components = n_components
        self.x_mean: np.ndarray | None = None
        self.y_mean: float | None = None
        self.weights: list[np.ndarray] = []
        self.loadings: list[np.ndarray] = []
        self.coefficients: list[float] = []

    def fit(self, x: np.ndarray, y: np.ndarray) -> "PLS1":
        x_work = x.astype(float).copy()
        y_work = y.astype(float).copy()
        self.x_mean = x_work.mean(axis=0)
        self.y_mean = float(y_work.mean())
        x_work -= self.x_mean
        y_work -= self.y_mean

        for _ in range(self.n_components):
            weight = x_work.T @ y_work
            norm = np.linalg.norm(weight)
            if norm < 1e-12:
                break
            weight /= norm
            scores = x_work @ weight
            score_ss = float(scores @ scores)
            if score_ss < 1e-12:
                break
            loading = x_work.T @ scores / score_ss
            coefficient = float(y_work @ scores / score_ss)
            x_work -= np.outer(scores, loading)
            y_work -= coefficient * scores
            self.weights.append(weight)
            self.loadings.append(loading)
            self.coefficients.append(coefficient)
        return self

    def predict(self, x: np.ndarray) -> np.ndarray:
        if self.x_mean is None or self.y_mean is None:
            raise RuntimeError("PLS model is not fitted")
        x_work = x.astype(float) - self.x_mean
        prediction = np.full(x.shape[0], self.y_mean, dtype=float)
        for weight, loading, coefficient in zip(
            self.weights, self.loadings, self.coefficients
        ):
            scores = x_work @ weight
            prediction += coefficient * scores
            x_work -= np.outer(scores, loading)
        return prediction


def fit_global_ds(
    slave: np.ndarray,
    master: np.ndarray,
    ridge: float = 0.35,
) -> tuple[np.ndarray, np.ndarray]:
    """Fit an affine map slave -> master using ridge regression."""
    slave_mean = slave.mean(axis=0)
    master_mean = master.mean(axis=0)
    xs = slave - slave_mean
    ym = master - master_mean
    gram = xs.T @ xs + ridge * np.eye(xs.shape[1])
    transform = np.linalg.solve(gram, xs.T @ ym)
    return transform, slave_mean, master_mean  # type: ignore[return-value]


def apply_global_ds(
    spectra: np.ndarray,
    transform: np.ndarray,
    slave_mean: np.ndarray,
    master_mean: np.ndarray,
) -> np.ndarray:
    return (spectra - slave_mean) @ transform + master_mean


def fit_pds(
    slave: np.ndarray,
    master: np.ndarray,
    window: int = 21,
    step: int = 5,
    ridge: float = 1.2,
) -> list[dict]:
    if window % 2 == 0:
        raise ValueError("PDS window must be odd")
    half = window // 2
    models = []
    for start in range(0, slave.shape[1], step):
        a = max(0, start - half)
        b = min(slave.shape[1], start + half + 1)
        if b - a < 7:
            continue
        xs = slave[:, a:b]
        ym = master[:, a:b]
        xs_mean = xs.mean(axis=0)
        ym_mean = ym.mean(axis=0)
        xs_centered = xs - xs_mean
        ym_centered = ym - ym_mean
        transform = np.linalg.solve(
            xs_centered.T @ xs_centered + ridge * np.eye(b - a),
            xs_centered.T @ ym_centered,
        )
        models.append(
            {
                "start": a,
                "stop": b,
                "transform": transform,
                "xs_mean": xs_mean,
                "ym_mean": ym_mean,
            }
        )
    return models


def apply_pds(spectra: np.ndarray, models: Iterable[dict]) -> np.ndarray:
    numerator = np.zeros_like(spectra, dtype=float)
    denominator = np.zeros(spectra.shape[1], dtype=float)
    for model in models:
        a, b = model["start"], model["stop"]
        mapped = (
            (spectra[:, a:b] - model["xs_mean"]) @ model["transform"]
            + model["ym_mean"]
        )
        numerator[:, a:b] += mapped
        denominator[a:b] += 1.0
    denominator[denominator == 0] = 1
    return numerator / denominator


def slope_bias_correction(
    predicted_transfer: np.ndarray,
    reference_transfer: np.ndarray,
) -> tuple[float, float]:
    design = np.column_stack([predicted_transfer, np.ones_like(predicted_transfer)])
    slope, intercept = np.linalg.lstsq(design, reference_transfer, rcond=None)[0]
    return float(slope), float(intercept)


def regression_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    residual = y_pred - y_true
    rmsep = float(np.sqrt(np.mean(residual**2)))
    mae = float(np.mean(np.abs(residual)))
    denominator = float(np.sum((y_true - y_true.mean()) ** 2))
    r2 = float(1.0 - np.sum(residual**2) / denominator) if denominator else 0.0
    return {
        "rmsep": rmsep,
        "mae": mae,
        "r2": r2,
        "max_abs_error": float(np.max(np.abs(residual))),
    }


SEGMENT_LABELS = ("low", "mid", "high")


def residual_by_segment(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    labels: tuple[str, ...] = SEGMENT_LABELS,
) -> list[dict[str, float | str | int]]:
    """Split samples by reference concentration and report bias/error per segment.

    A single RMSEP can hide a method that is accurate on average while biased at
    the low or high concentration end, so the residual structure is reported per
    segment instead of only as one aggregate number.
    """
    residual = y_pred - y_true
    order = np.argsort(y_true, kind="stable")
    segments = np.array_split(order, len(labels))
    rows: list[dict[str, float | str | int]] = []
    for label, index in zip(labels, segments):
        if index.size == 0:
            continue
        part = residual[index]
        rows.append(
            {
                "segment": label,
                "n": int(index.size),
                "mean_bias": float(np.mean(part)),
                "rmsep": float(np.sqrt(np.mean(part**2))),
            }
        )
    return rows


REQUIRED_METADATA = {
    "sample_id",
    "batch_id",
    "instrument_id",
    "acquired_at",
    "wavelength_start_nm",
    "wavelength_end_nm",
    "points",
    "unit",
    "preprocess",
    "sha256",
    "calibration_id",
    "model_version",
}


def check_metadata(record: dict) -> list[str]:
    errors: list[str] = []
    missing = REQUIRED_METADATA - set(record)
    if missing:
        errors.append(f"missing fields: {sorted(missing)}")
    if record.get("unit") not in {"absorbance", "a.u.", "reflectance"}:
        errors.append("unit must be absorbance, reflectance, or a.u.")
    if not isinstance(record.get("points"), int) or record.get("points", 0) <= 0:
        errors.append("points must be a positive integer")
    start = record.get("wavelength_start_nm")
    stop = record.get("wavelength_end_nm")
    if not (isinstance(start, (int, float)) and isinstance(stop, (int, float)) and stop > start):
        errors.append("wavelength_end_nm must be greater than wavelength_start_nm")
    sha = str(record.get("sha256", ""))
    if not re.fullmatch(r"[0-9a-f]{64}", sha):
        errors.append("sha256 must be a 64-character lowercase hex digest")
    try:
        datetime.fromisoformat(str(record.get("acquired_at", "")).replace("Z", "+00:00"))
    except ValueError:
        errors.append("acquired_at must be ISO 8601")
    return errors


def sha256_array(array: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(array).tobytes()).hexdigest()


def write_csv(path: Path, header: list[str], rows: Iterable[list]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(rows)


def save_arrays(
    train: SpectralDataset,
    transfer: SpectralDataset,
    test: SpectralDataset,
) -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        DATA / "master_train.npz",
        wavelengths=train.wavelengths,
        spectra=train.x_master,
        y=train.y,
    )
    np.savez_compressed(
        DATA / "transfer_pairs.npz",
        wavelengths=transfer.wavelengths,
        master=transfer.x_master,
        slave=transfer.x_slave,
        y=transfer.y,
    )
    np.savez_compressed(
        DATA / "independent_target_test.npz",
        wavelengths=test.wavelengths,
        spectra=test.x_slave,
        y=test.y,
    )


def make_metadata_manifest(
    train: SpectralDataset,
    transfer: SpectralDataset,
    test: SpectralDataset,
) -> dict:
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    records = [
        {
            "sample_id": sample_id,
            "batch_id": "MASTER-TRAIN",
            "instrument_id": "MASTER-A",
            "acquired_at": now,
            "wavelength_start_nm": float(train.wavelengths[0]),
            "wavelength_end_nm": float(train.wavelengths[-1]),
            "points": int(train.wavelengths.size),
            "unit": "absorbance",
            "preprocess": "raw;mean-centering-in-model",
            "sha256": sha256_array(train.x_master[index]),
            "calibration_id": "CAL-A-2026-10",
            "model_version": "ch14-demo-1.0.0",
        }
        for index, sample_id in enumerate(train.sample_ids)
    ]
    records += [
        {
            "sample_id": sample_id,
            "batch_id": "TRANSFER-2026-10",
            "instrument_id": "SLAVE-B",
            "acquired_at": now,
            "wavelength_start_nm": float(transfer.wavelengths[0]),
            "wavelength_end_nm": float(transfer.wavelengths[-1]),
            "points": int(transfer.wavelengths.size),
            "unit": "absorbance",
            "preprocess": "raw;paired-for-DS-PDS",
            "sha256": sha256_array(transfer.x_slave[index]),
            "calibration_id": "CAL-B-2026-10",
            "model_version": "ch14-demo-1.0.0",
        }
        for index, sample_id in enumerate(transfer.sample_ids)
    ]
    records += [
        {
            "sample_id": sample_id,
            "batch_id": "INDEPENDENT-TEST-2026-11",
            "instrument_id": "SLAVE-B",
            "acquired_at": now,
            "wavelength_start_nm": float(test.wavelengths[0]),
            "wavelength_end_nm": float(test.wavelengths[-1]),
            "points": int(test.wavelengths.size),
            "unit": "absorbance",
            "preprocess": "raw;no-transfer-fitting",
            "sha256": sha256_array(test.x_slave[index]),
            "calibration_id": "CAL-B-2026-10",
            "model_version": "ch14-demo-1.0.0",
        }
        for index, sample_id in enumerate(test.sample_ids)
    ]
    manifest = {
        "schema_version": "ch14-metadata-1.0",
        "created_at": now,
        "scope": "synthetic teaching data only",
        "records": records,
    }
    validation_errors = [
        {"sample_id": record["sample_id"], "errors": check_metadata(record)}
        for record in records
    ]
    manifest["validation_errors"] = [
        row for row in validation_errors if row["errors"]
    ]
    return manifest


def save_figure(
    wavelengths: np.ndarray,
    transfer: SpectralDataset,
    y_true: np.ndarray,
    predictions: dict[str, np.ndarray],
) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(12.5, 8.4))
    ax = axes[0, 0]
    ax.plot(wavelengths, transfer.x_master[0], label="master", lw=1.8, color="#38678f")
    ax.plot(wavelengths, transfer.x_slave[0], label="slave", lw=1.8, color="#d97706")
    ax.set_title("Same sample: instrument response difference")
    ax.set_xlabel("wavelength (nm)")
    ax.set_ylabel("absorbance")
    ax.legend(frameon=False)
    ax.grid(alpha=0.2)

    ax = axes[0, 1]
    colors = {
        "Direct slave use": "#9aa7b4",
        "Slope/bias": "#7b61a8",
        "Global DS": "#2f7f86",
        "PDS": "#e56b4a",
    }
    for name, prediction in predictions.items():
        metrics = regression_metrics(y_true, prediction)
        ax.scatter(y_true, prediction, s=17, alpha=0.58, label=f"{name}: RMSEP={metrics['rmsep']:.3f}", color=colors[name])
    low, high = 0.0, 1.0
    ax.plot([low, high], [low, high], "k--", lw=1)
    ax.set_xlim(low, high)
    ax.set_ylim(low, high)
    ax.set_xlabel("reference concentration")
    ax.set_ylabel("predicted concentration")
    ax.set_title("Independent target-domain validation")
    ax.legend(frameon=False, fontsize=8)
    ax.grid(alpha=0.2)

    ax = axes[1, 0]
    for name, prediction in predictions.items():
        ax.scatter(y_true, prediction - y_true, s=14, alpha=0.55, label=name, color=colors[name])
    ax.axhline(0, color="k", ls="--", lw=1)
    ax.set_xlabel("reference concentration")
    ax.set_ylabel("prediction residual")
    ax.set_title("Residual structure matters, not only average error")
    ax.legend(frameon=False, fontsize=8)
    ax.grid(alpha=0.2)

    ax = axes[1, 1]
    names = list(predictions)
    rmsep = [regression_metrics(y_true, predictions[name])["rmsep"] for name in names]
    bars = ax.bar(range(len(names)), rmsep, color=[colors[name] for name in names])
    ax.set_xticks(range(len(names)), [name.replace(" ", "\n") for name in names], fontsize=8)
    ax.set_ylabel("RMSEP")
    ax.set_title("Lower is better on independent target data")
    ax.grid(axis="y", alpha=0.2)
    for bar, value in zip(bars, rmsep):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"{value:.3f}", ha="center", va="bottom", fontsize=8)
    fig.tight_layout()
    fig.savefig(RESULTS / "ch14_transfer_performance.png", dpi=220)
    plt.close(fig)


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)
    train, transfer, test, _ = generate_case()
    save_arrays(train, transfer, test)

    pls = PLS1(n_components=9).fit(train.x_master, train.y)
    y_direct = pls.predict(test.x_slave)

    y_transfer_direct = pls.predict(transfer.x_slave)
    slope, intercept = slope_bias_correction(y_transfer_direct, transfer.y)
    y_slope_bias = slope * y_direct + intercept

    transform, slave_mean, master_mean = fit_global_ds(
        transfer.x_slave, transfer.x_master, ridge=0.18
    )
    x_ds = apply_global_ds(test.x_slave, transform, slave_mean, master_mean)
    y_ds = pls.predict(x_ds)

    pds_models = fit_pds(
        transfer.x_slave, transfer.x_master, window=25, step=5, ridge=0.35
    )
    x_pds = apply_pds(test.x_slave, pds_models)
    y_pds = pls.predict(x_pds)

    predictions = {
        "Direct slave use": y_direct,
        "Slope/bias": y_slope_bias,
        "Global DS": y_ds,
        "PDS": y_pds,
    }
    metrics = {
        name: regression_metrics(test.y, prediction)
        for name, prediction in predictions.items()
    }
    segment_metrics = {
        name: residual_by_segment(test.y, prediction)
        for name, prediction in predictions.items()
    }

    save_figure(train.wavelengths, transfer, test.y, predictions)

    rows = []
    for sample_id, reference, direct, slope_bias, ds, pds in zip(
        test.sample_ids,
        test.y,
        y_direct,
        y_slope_bias,
        y_ds,
        y_pds,
    ):
        rows.append(
            [
                sample_id,
                f"{reference:.6f}",
                f"{direct:.6f}",
                f"{slope_bias:.6f}",
                f"{ds:.6f}",
                f"{pds:.6f}",
            ]
        )
    write_csv(
        RESULTS / "independent_test_predictions.csv",
        ["sample_id", "reference", "direct_slave", "slope_bias", "DS", "PDS"],
        rows,
    )

    metric_rows = [
        [name, *[f"{value:.6f}" for value in metric.values()]]
        for name, metric in metrics.items()
    ]
    write_csv(
        RESULTS / "transfer_metrics.csv",
        ["method", "rmsep", "mae", "r2", "max_abs_error"],
        metric_rows,
    )

    segment_rows = []
    for name, segments in segment_metrics.items():
        for segment in segments:
            segment_rows.append(
                [
                    name,
                    segment["segment"],
                    segment["n"],
                    f"{segment['mean_bias']:.6f}",
                    f"{segment['rmsep']:.6f}",
                ]
            )
    write_csv(
        RESULTS / "residual_by_segment.csv",
        ["method", "segment", "n", "mean_bias", "rmsep"],
        segment_rows,
    )

    manifest = make_metadata_manifest(train, transfer, test)
    (RESULTS / "metadata_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    summary = {
        "seed": 42,
        "n_train": int(train.x_master.shape[0]),
        "n_transfer": int(transfer.x_slave.shape[0]),
        "n_independent_test": int(test.x_slave.shape[0]),
        "wavelength_range_nm": [float(train.wavelengths[0]), float(train.wavelengths[-1])],
        "pls_components": pls.n_components,
        "global_ds_ridge": 0.18,
        "pds_window": 25,
        "pds_step": 5,
        "pds_ridge": 0.35,
        "slope_bias": {"slope": slope, "intercept": intercept},
        "metrics": metrics,
        "residual_by_segment": segment_metrics,
        "metadata_validation_error_count": len(manifest["validation_errors"]),
    }
    (RESULTS / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print("=== Chapter 14 calibration-transfer exercise ===")
    print(
        f"Samples: train={summary['n_train']}, transfer={summary['n_transfer']}, "
        f"independent test={summary['n_independent_test']}"
    )
    for name, metric in metrics.items():
        print(
            f"{name:18s} RMSEP={metric['rmsep']:.4f} "
            f"MAE={metric['mae']:.4f} R2={metric['r2']:.4f}"
        )

    print("Residual structure by concentration segment (bias / RMSEP):")
    for name, segments in segment_metrics.items():
        detail = "  ".join(
            f"{segment['segment']}={segment['mean_bias']:+.4f}/{segment['rmsep']:.4f}"
            for segment in segments
        )
        print(f"  {name:18s} {detail}")

    print(f"Metadata validation errors: {summary['metadata_validation_error_count']}")
    print(f"Saved: {RESULTS / 'ch14_transfer_performance.png'}")


if __name__ == "__main__":
    main()

