"""Plot every paired movie-level IoU from the archived synthetic LPTEM example.

From the repository root (dependency: Matplotlib and its dependencies):
    python code/ch07_exercises/plot_lptem_pairs.py

No model is trained. Input is the 32 archived numerical records; movie IDs are
local to each condition. The same ID across conditions is not the same movie.
All 16 movie pairs are retained. Points are observations, not means; no error
bars or statistical tests are added. SVG text remains editable.
"""

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from statistics import mean
import sys


ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / "resources/annual/2026-2027/results/ch07/lptem/metrics.csv"
OUTPUT = ROOT / "assets/figures/ch07_lptem_pairs.svg"
CONDITIONS = ("in_distribution", "shifted")
METHODS = ("Local mean", "CNN")
FIELDS = ("condition", "method", "threshold", "movie", "iou", "dice", "foreground_area_mae_px2")


def load_pairs(path):
    """Validate the fixed archive protocol; never silently omit or merge rows."""
    with Path(path).open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != list(FIELDS):
            raise ValueError("Unexpected metric columns")
        records = list(reader)
    expected = {(condition, method, movie)
                for condition in CONDITIONS for method in METHODS for movie in range(1, 9)}
    observed = {}
    for row in records:
        if set(row) != set(FIELDS) or None in row.values():
            raise ValueError("Malformed metric row")
        movie = int(row["movie"])
        key = (row["condition"], row["method"], movie)
        if key not in expected or key in observed:
            raise ValueError(f"Unexpected or duplicate movie metric: {key}")
        iou = float(row["iou"])
        if not math.isfinite(iou) or not 0 <= iou <= 1:
            raise ValueError(f"Invalid IoU: {key}")
        observed[key] = iou
    if set(observed) != expected or len(records) != 32:
        raise ValueError("Expected both methods on eight movies per condition (32 rows)")
    return {condition: [(movie, observed[(condition, "Local mean", movie)],
                        observed[(condition, "CNN", movie)]) for movie in range(1, 9)]
            for condition in CONDITIONS}


def summarize(pairs, source):
    result = {"source_file": Path(source).name,
              "source_sha256": hashlib.sha256(Path(source).read_bytes()).hexdigest(),
              "metric_records": 32, "data_type": "synthetic teaching movies", "conditions": {}}
    for condition, data in pairs.items():
        difference = [cnn - local for _, local, cnn in data]
        result["conditions"][condition] = {
            "movies": len(data), "cnn_higher": sum(value > 0 for value in difference),
            "mean_local_iou": mean(local for _, local, _ in data),
            "mean_cnn_iou": mean(cnn for _, _, cnn in data),
            "paired_difference_min": min(difference), "paired_difference_max": max(difference),
        }
    return result


def draw(pairs, output, qa_dir=None, audit_tools=None):
    import matplotlib as mpl
    mpl.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    mpl.rcParams.update({
        "font.family": "sans-serif", "font.sans-serif": ["Arial", "DejaVu Sans"],
        "font.size": 9, "axes.labelsize": 9, "xtick.labelsize": 8,
        "ytick.labelsize": 8, "legend.fontsize": 9, "svg.fonttype": "none",
        "svg.hashsalt": "ch07-lptem-pairs",
        "pdf.fonttype": 42, "axes.spines.top": False, "axes.spines.right": False,
        "axes.linewidth": 0.7,
    })
    local_color, cnn_color = "#737D87", "#177B93"
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 4.2), sharex=True, sharey=True)
    fig.subplots_adjust(left=0.095, right=0.98, bottom=0.22, top=0.74, wspace=0.25)
    titles = ("In-distribution", "Lower contrast + higher noise")
    for index, (axis, condition, title) in enumerate(zip(axes, CONDITIONS, titles)):
        data = pairs[condition]
        movies = [movie for movie, _, _ in data]
        local = [value for _, value, _ in data]
        cnn = [value for _, _, value in data]
        for movie, left, right in data:
            axis.plot([left, right], [movie, movie], color="#A9AFB4", lw=1.1, zorder=1)
        axis.scatter(local, movies, s=29, marker="o", facecolor="white", edgecolor=local_color,
                     linewidth=1.1, zorder=2)
        axis.scatter(cnn, movies, s=19, marker="D", color=cnn_color, linewidth=0.5, zorder=3)
        axis.set(xlim=(0, 1), ylim=(8.6, 0.4), xlabel="Foreground IoU")
        axis.set_xticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
        axis.set_yticks(movies, [str(movie) for movie in movies])
        axis.tick_params(axis="y", labelleft=True, length=0, pad=5)
        axis.grid(axis="x", color="#E2E5E7", linewidth=0.65, zorder=0)
        axis.set_axisbelow(True)
        axis.set_title(title, fontsize=10, pad=30)
        higher = sum(right > left for _, left, right in data)
        axis.text(0.5, 1.035, f"CNN higher: {higher}/8 movies", transform=axis.transAxes,
                  ha="center", va="bottom", fontsize=9)
        axis.annotate(chr(ord("a") + index), xy=(0, 1), xycoords="axes fraction",
                      xytext=(-24, 30), textcoords="offset points", ha="left", va="baseline",
                      fontsize=11, fontweight="bold")
    axes[0].set_ylabel("Movie ID (within condition)", labelpad=8)
    fig.suptitle("Synthetic LPTEM: paired foreground IoU", fontsize=12, fontweight="bold", y=0.98)
    handles = [
        Line2D([], [], marker="o", color="none", markerfacecolor="white",
               markeredgecolor=local_color, markeredgewidth=1.1, markersize=5.4, label="Local mean"),
        Line2D([], [], marker="D", color="none", markerfacecolor=cnn_color,
               markeredgecolor=cnn_color, markersize=4.4, label="CNN"),
    ]
    fig.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, 0.94),
               ncol=2, frameon=False, handlelength=1, columnspacing=2.5, handletextpad=0.6)
    fig.text(0.5, 0.055, "Each row pairs two methods on one simulated movie; conditions use different movies.",
             ha="center", va="center", fontsize=8)
    fig.canvas.draw()

    # Canvas measurements provide a standalone guard without a maintainer tool.
    rectangles = [axis.get_window_extent().transformed(fig.dpi_scale_trans.inverted()).bounds
                  for axis in axes]
    for component in (1, 2, 3):
        if abs(rectangles[0][component] - rectangles[1][component]) * 72 > 1.5:
            raise RuntimeError("Comparable plot areas differ by more than 1.5 pt")
    if audit_tools is not None:
        if qa_dir is None:
            raise ValueError("--audit-tools requires --qa-dir")
        sys.path.insert(0, str(audit_tools))
        from audit_panel_alignment import require_matplotlib_panel_alignment
        require_matplotlib_panel_alignment(
            fig, json_out=qa_dir / "ch07_lptem_pairs.alignment.json",
            overlay_svg=qa_dir / "ch07_lptem_pairs.alignment.svg", strict=True,
            require_panel_labels=True, tolerance_pt=1.5, gutter_tolerance_pt=1.5,
        )
    output.parent.mkdir(parents=True, exist_ok=True)
    metadata = {"Date": None, "Creator": "G07 reproducible synthetic LPTEM metric plot"}
    fig.savefig(output, format="svg", metadata=metadata)
    # Matplotlib's multiline SVG path attributes can include trailing spaces.
    # Normalize text whitespace only; keep every path coordinate and command.
    svg_lines = output.read_text(encoding="utf-8").splitlines()
    output.write_bytes(("\n".join(line.rstrip() for line in svg_lines) + "\n").encode("utf-8"))
    if qa_dir is not None:
        fig.savefig(qa_dir / "ch07_lptem_pairs.pdf", metadata={"CreationDate": None, "ModDate": None})
        fig.savefig(qa_dir / "ch07_lptem_pairs.png", dpi=300)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, default=INPUT)
    parser.add_argument("--out", type=Path, default=OUTPUT, help="editable SVG output")
    parser.add_argument("--qa-dir", type=Path, help="optional PDF, PNG and numerical summary directory")
    parser.add_argument("--audit-tools", type=Path, help="optional maintainer alignment-auditor directory")
    args = parser.parse_args()
    if args.out.suffix.lower() != ".svg":
        parser.error("--out must end with .svg")
    if args.audit_tools is not None and args.qa_dir is None:
        parser.error("--audit-tools requires --qa-dir")
    pairs = load_pairs(args.csv)
    summary = summarize(pairs, args.csv)
    if args.qa_dir is not None:
        args.qa_dir.mkdir(parents=True, exist_ok=True)
    draw(pairs, args.out, args.qa_dir, args.audit_tools)
    if args.qa_dir is not None:
        (args.qa_dir / "ch07_lptem_pairs.summary.json").write_text(
            json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    print("Wrote editable SVG. All 32 archived rows retained; no model training performed.")


if __name__ == "__main__":
    main()
