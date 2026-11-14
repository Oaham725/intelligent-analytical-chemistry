"""Verify the archived default ch07 experiment without training or third-party packages.

Run from the repository root: python code/ch07_exercises/verify_results.py
This checks the fixed teaching protocol, not arbitrary experiment configurations.
LPTEM checks recompute averages from per-movie metrics, not masks from raw images.
"""

import argparse
import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean


DEFAULT_ARCHIVE = Path(__file__).resolve().parents[2] / "resources/annual/2026-2027/results/ch07"
MODELS = {"logistic": 195, "mlp": 2179, "cnn": 1819, "transformer": 3331}
SEEDS = (7, 19, 42)
RUN_KEYS = {(m, s) for m in MODELS for s in SEEDS}
CONDITIONS = ("in_distribution", "shifted")
METHODS = ("Local mean", "CNN")
FILES = ("spectra/metrics.json", "spectra/history.csv", "spectra/predictions.csv",
         "lptem/metrics.csv", "lptem/training.csv", "summary.json")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load_json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, f"{path.name}: duplicate JSON key {key}")
            result[key] = value
        return result
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique)


def rows(path, fields):
    with path.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        require(reader.fieldnames == fields.split(","), f"{path.name}: unexpected CSV columns")
        result = list(reader)
    require(all(set(row) == set(reader.fieldnames) and None not in row.values() for row in result),
            f"{path.name}: malformed CSV record")
    return result


def integer(value, context):
    number = int(value)
    require(str(number) == str(value), f"{context}: expected integer")
    return number


def finite(value, context, low=0, high=None):
    number = float(value)
    require(math.isfinite(number) and number >= low and (high is None or number <= high),
            f"{context}: invalid numeric value")
    return number


def same(actual, expected, context, atol=1e-10):
    """Compare every key/element, with a tight tolerance only for floats."""
    if isinstance(expected, dict):
        require(isinstance(actual, dict) and set(actual) == set(expected), f"{context}: keys differ")
        for key in expected:
            same(actual[key], expected[key], f"{context}.{key}", atol)
    elif isinstance(expected, list):
        require(isinstance(actual, list) and len(actual) == len(expected), f"{context}: length differs")
        for index, (a, e) in enumerate(zip(actual, expected)):
            same(a, e, f"{context}[{index}]", atol)
    elif isinstance(expected, float):
        require(isinstance(actual, (int, float)) and math.isfinite(actual)
                and math.isclose(actual, expected, rel_tol=0, abs_tol=atol), f"{context}: value differs")
    else:
        require(actual == expected, f"{context}: value differs")


def score(records):
    matrix = [[0] * 3 for _ in range(3)]
    for row in records:
        matrix[row["actual"]][row["predicted"]] += 1
    f1 = []
    for k in range(3):
        denominator = sum(matrix[k]) + sum(row[k] for row in matrix)
        f1.append(2 * matrix[k][k] / denominator if denominator else 0.0)
    return {"accuracy": sum(matrix[k][k] for k in range(3)) / len(records),
            "macro_f1": mean(f1), "confusion_matrix": matrix}


def verify_spectra(root):
    report = load_json(root / "spectra/metrics.json")
    same(report["data_seed"], 2026, "data seed")
    same(report["batches"], {"train": list(range(6)), "validation": [6, 7], "test": [8, 9, 10, 11]},
         "batch partition")
    if "dataset_summary" in report:
        same(report["dataset_summary"], {
            "train": {"samples": 144, "scans": 288, "batches": list(range(6)), "scans_per_sample": 2},
            "validation": {"samples": 48, "scans": 96, "batches": [6, 7], "scans_per_sample": 2},
            "test": {"samples": 96, "scans": 192, "batches": [8, 9, 10, 11], "scans_per_sample": 2}},
            "dataset summary")
    records = rows(root / "spectra/predictions.csv", "model,seed,batch,sample,actual,predicted,p0,p1,p2")
    require(len(records) == 1152, "spectra: expected 1152 prediction records")
    groups, seen, metadata = defaultdict(list), set(), {}
    for row in records:
        for key in ("seed", "batch", "sample", "actual", "predicted"):
            row[key] = integer(row[key], key)
        run = (row["model"], row["seed"])
        key = (*run, row["sample"])
        require(run in RUN_KEYS and key not in seen, "spectra: unexpected run or duplicate sample prediction")
        seen.add(key)
        require(192 <= row["sample"] < 288 and row["batch"] == row["sample"] // 24,
                "spectra: sample ID / batch mismatch")
        require(row["actual"] in range(3) and row["predicted"] in range(3), "spectra: invalid class")
        label = (row["batch"], row["actual"])
        require(metadata.setdefault(row["sample"], label) == label,
                "spectra: inconsistent sample label or batch across runs")
        probability = [finite(row[f"p{k}"], "probability", high=1) for k in range(3)]
        require(abs(sum(probability) - 1) <= 1e-6, "spectra: probabilities do not sum to one")
        require(row["predicted"] == max(range(3), key=probability.__getitem__),
                "spectra: prediction differs from probability argmax")
        groups[run].append(row)
    require(set(groups) == RUN_KEYS, "spectra: missing model/seed combination")
    for run, sample_rows in groups.items():
        require({r["sample"] for r in sample_rows} == set(range(192, 288)), f"{run}: missing sample")
        require(Counter((r["batch"], r["actual"]) for r in sample_rows)
                == Counter({(b, c): 8 for b in range(8, 12) for c in range(3)}),
                f"{run}: expected 24 samples per batch and eight per class")

    history = rows(root / "spectra/history.csv", "model,seed,epoch,train_scan_nll,validation_sample_nll")
    require(len(history) == 360, "spectra: expected 360 history records")
    histories, history_keys = defaultdict(dict), set()
    for row in history:
        run = (row["model"], integer(row["seed"], "history seed"))
        epoch = integer(row["epoch"], "history epoch")
        key = (*run, epoch)
        require(run in RUN_KEYS and epoch in range(1, 31) and key not in history_keys,
                "spectra: duplicate/unexpected history record")
        history_keys.add(key)
        finite(row["train_scan_nll"], "training loss")
        histories[run][epoch] = finite(row["validation_sample_nll"], "validation loss")
    require(history_keys == {(*run, e) for run in RUN_KEYS for e in range(1, 31)},
            "spectra: incomplete training history")

    runs = report["runs"]
    require(len(runs) == 12, "spectra: expected 12 metric records")
    metric_keys, computed = set(), {}
    for run_report in runs:
        key = (run_report["model"], run_report["seed"])
        require(key in RUN_KEYS and key not in metric_keys, "spectra: duplicate/unexpected metric run")
        metric_keys.add(key)
        require(run_report["parameters"] == MODELS[key[0]], "spectra: parameter count differs")
        best_epoch = min(range(1, 31), key=lambda e: histories[key][e])
        require(run_report["epoch"] == best_epoch, "spectra: selected epoch is not first minimum validation loss")
        sample_rows = groups[key]
        subsets = {"all": sample_rows, "nominal": [r for r in sample_rows if r["batch"] < 10],
                   "shifted": [r for r in sample_rows if r["batch"] >= 10]}
        subsets.update({f"batch_{b}": [r for r in sample_rows if r["batch"] == b] for b in range(8, 12)})
        computed[key] = {part: score(rr) for part, rr in subsets.items()}
        same(run_report["test"], computed[key], f"spectra metrics {key}")

    summary = {}
    for model in MODELS:
        summary[model] = {part: {
            metric: mean(computed[(model, seed)][part][metric] for seed in SEEDS)
            for metric in ("accuracy", "macro_f1")}
            for part in ("all", "nominal", "shifted")}
    return summary


def verify_lptem(root):
    data = rows(root / "lptem/metrics.csv", "condition,method,threshold,movie,iou,dice,foreground_area_mae_px2")
    require(len(data) == 32, "LPTEM: expected 32 movie metrics")
    seen, groups, thresholds = set(), defaultdict(list), {}
    expected = {(c, m, i) for c in CONDITIONS for m in METHODS for i in range(1, 9)}
    for row in data:
        key = (row["condition"], row["method"], integer(row["movie"], "movie"))
        require(key in expected and key not in seen, "LPTEM: duplicate/unexpected movie metric")
        seen.add(key)
        threshold = finite(row["threshold"], "threshold", high=1)
        require(thresholds.setdefault(key[1], threshold) == threshold,
                "LPTEM: validation threshold changed across test movies")
        iou = finite(row["iou"], "IoU", high=1)
        dice = finite(row["dice"], "Dice", high=1)
        area = finite(row["foreground_area_mae_px2"], "area MAE", high=48 * 48)
        same(dice, 2 * iou / (1 + iou), "Dice/IoU identity")
        groups[key[:2]].append({"iou": iou, "dice": dice, "foreground_area_mae_px2": area})
    require(seen == expected, "LPTEM: missing movie metric")
    training = rows(root / "lptem/training.csv", "epoch,weighted_bce")
    require(len(training) == 20, "LPTEM: expected 20 training epochs")
    epochs = [integer(row["epoch"], "LPTEM epoch") for row in training]
    require(epochs == list(range(1, 21)), "LPTEM: training epochs missing, duplicated or out of order")
    losses = [finite(row["weighted_bce"], "weighted BCE") for row in training]
    summary = {f"{c}/{m}": {field: mean(r[field] for r in group) for field in group[0]}
               for (c, m), group in groups.items()}
    return summary, {"first_weighted_bce": losses[0], "last_weighted_bce": losses[-1]}


def recompute(root):
    """Validate records and compute a summary independently of summary.json and checksums."""
    spectra = verify_spectra(root)
    lptem, training = verify_lptem(root)
    # Published table values: rounding these computed means must reproduce the teaching notes.
    spectra_table = {"logistic": (0.955, 0.979, 0.930), "mlp": (0.948, 0.979, 0.918),
                     "cnn": (0.955, 0.993, 0.918), "transformer": (0.962, 0.993, 0.930)}
    for model, values in spectra_table.items():
        for part, value in zip(("all", "nominal", "shifted"), values):
            require(round(spectra[model][part]["macro_f1"], 3) == value, "spectra: published table differs")
    lptem_table = {"in_distribution/Local mean": (0.636, 0.772, 26.6),
                   "in_distribution/CNN": (0.673, 0.801, 25.7),
                   "shifted/Local mean": (0.265, 0.400, 69.2), "shifted/CNN": (0.255, 0.389, 68.6)}
    for key, values in lptem_table.items():
        actual = lptem[key]
        require((round(actual["iou"], 3), round(actual["dice"], 3),
                 round(actual["foreground_area_mae_px2"], 1)) == values, "LPTEM: published table differs")
    return {"spectra": spectra, "lptem": lptem, "lptem_training": training,
            "record_counts": {"spectra_runs": 12, "spectra_predictions": 1152,
                              "spectra_history": 360, "lptem_metrics": 32, "lptem_training": 20}}


def verify(root, check_hashes=True):
    root = Path(root)
    computed = recompute(root)
    same(load_json(root / "summary.json"), computed, "summary.json")
    if check_hashes:
        manifest = load_json(root / "manifest.json")
        require(manifest["schema_version"] == 1, "unsupported manifest version")
        require(set(manifest["sha256"]) == set(FILES), "manifest: unexpected/missing files")
        for name in FILES:
            digest = hashlib.sha256((root / name).read_bytes()).hexdigest()
            require(digest == manifest["sha256"][name], f"SHA-256 mismatch: {name}")
    return computed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, default=DEFAULT_ARCHIVE)
    parser.add_argument("--write-summary", type=Path, help="write a recomputed summary after full verification")
    args = parser.parse_args()
    try:
        summary = verify(args.archive)
    except (ValueError, KeyError, TypeError, OSError, csv.Error) as error:
        parser.exit(1, f"FAIL: {error}\n")
    if args.write_summary:
        args.write_summary.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print("PASS: 12 spectra runs, 1152 predictions, 360 history rows; 32 LPTEM metrics, 20 training rows.")
    print("All recomputed metrics, published rounding, summary and SHA-256 checks passed. No training performed.")


if __name__ == "__main__":
    main()
