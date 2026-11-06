"""Synthetic liquid-phase TEM-like foreground segmentation on a CPU."""

import argparse
import csv
from pathlib import Path

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view


FRAME_COUNT = 8
SIZE = 48
WINDOW = 5


def simulate(rng, sequence_count, shifted=False):
    """Return noisy images and foreground masks, grouped by movie."""
    row, col = np.mgrid[:SIZE, :SIZE]
    images = np.empty((sequence_count, FRAME_COUNT, SIZE, SIZE), dtype=np.float32)
    masks = np.empty(images.shape, dtype=bool)
    for movie in range(sequence_count):
        centers = np.array([[13, 13], [15, 34], [33, 23]], dtype=float)
        centers += rng.uniform(-2, 2, centers.shape)
        drift = rng.uniform(-0.45, 0.45, centers.shape)
        radii = rng.uniform(2.7, 4.8, len(centers))
        growth = rng.uniform(0.05, 0.18, len(centers))
        phase = rng.uniform(0, 2 * np.pi)
        for frame in range(FRAME_COUNT):
            locations = centers + frame * drift
            radius = radii + frame * growth
            distance = np.hypot(
                row - locations[:, 0, None, None], col - locations[:, 1, None, None]
            )
            masks[movie, frame] = np.any(distance <= radius[:, None, None], axis=0)
            # Smooth edges and a spatially varying background imitate image nuisances.
            edge = np.clip((distance - radius[:, None, None]) / 0.65, -40, 40)
            contrast = (1 / (1 + np.exp(edge))).max(axis=0)
            background = 0.64 + 0.08 * np.sin(col / 9 + row / 14 + phase)
            amplitude, noise = (0.14, 0.17) if shifted else (0.28, 0.09)
            images[movie, frame] = background - amplitude * contrast + rng.normal(
                0, noise, (SIZE, SIZE)
            )
    return images, masks


def local_patches(images):
    """Unfold 5×5 windows; subtraction uses a fixed intensity reference."""
    padding = WINDOW // 2
    padded = np.pad(images, ((0, 0), (0, 0), (padding, padding), (padding, padding)),
                    mode="reflect")
    windows = sliding_window_view(padded, (WINDOW, WINDOW), axis=(-2, -1))
    return windows.reshape(-1, WINDOW * WINDOW) - np.float32(0.64)


def sigmoid(logits):
    return 1 / (1 + np.exp(-np.clip(logits, -40, 40)))


def train_cnn(patches, labels, rng):
    """Learn eight shared 5×5 filters and a 1×1 output convolution."""
    filters = rng.normal(0, 0.18, (WINDOW * WINDOW, 8)).astype(np.float32)
    biases = np.zeros(8, dtype=np.float32)
    readout = rng.normal(0, 0.18, 8).astype(np.float32)
    offset = np.zeros(1, dtype=np.float32)
    target = labels.ravel().astype(np.float32)
    weight = np.where(target > 0, (1 - target.mean()) / target.mean(), 1).astype(
        np.float32
    )
    history = []
    for epoch in range(1, 21):
        permutation = rng.permutation(target.size)
        for start in range(0, target.size, 4096):
            batch = permutation[start:start + 4096]
            x, y, w = patches[batch], target[batch], weight[batch]
            hidden = np.maximum(x @ filters + biases, 0)
            logits = hidden @ readout + offset
            residual = w * (sigmoid(logits) - y) / w.sum()
            hidden_gradient = residual[:, None] * readout * (hidden > 0)
            filters -= 0.1 * (x.T @ hidden_gradient)
            biases -= 0.1 * hidden_gradient.sum(axis=0)
            readout -= 0.1 * (hidden.T @ residual)
            offset -= 0.1 * residual.sum()
        logits = np.maximum(patches @ filters + biases, 0) @ readout + offset
        loss = np.average(np.logaddexp(0, logits) - target * logits, weights=weight)
        history.append((epoch, float(loss)))
    return (filters, biases, readout, offset), history


def scores(images, parameters):
    patches = local_patches(images)
    filters, biases, readout, offset = parameters
    baseline = -patches.mean(axis=1)
    cnn = sigmoid(np.maximum(patches @ filters + biases, 0) @ readout + offset)
    return {"Local mean": baseline.reshape(images.shape), "CNN": cnn.reshape(images.shape)}


def evaluate(prediction, truth):
    """Compute movie-level foreground overlap and mean area error."""
    axes = (1, 2, 3)
    intersection = np.sum(prediction & truth, axis=axes)
    union = np.sum(prediction | truth, axis=axes)
    total_area = prediction.sum(axis=axes) + truth.sum(axis=axes)
    iou = np.divide(intersection, union, out=np.ones_like(union, dtype=float), where=union > 0)
    dice = np.divide(2 * intersection, total_area,
                     out=np.ones_like(total_area, dtype=float), where=total_area > 0)
    area_error = prediction.sum(axis=(2, 3)) - truth.sum(axis=(2, 3))
    return iou, dice, np.abs(area_error).mean(axis=1)


def choose_threshold(score, truth):
    candidates = np.linspace(score.min(), score.max(), 81)
    validation_iou = [evaluate(score >= threshold, truth)[0].mean()
                      for threshold in candidates]
    return float(candidates[np.argmax(validation_iou)])


def plot_example(output, frame, truth, predictions):
    import matplotlib as mpl
    mpl.use("Agg")
    import matplotlib.pyplot as plt

    mpl.rcParams.update({"font.family": "sans-serif", "svg.fonttype": "none", "pdf.fonttype": 42, "font.size": 9})
    figure, axes = plt.subplots(1, 4, figsize=(7.4, 2.25))
    figure.subplots_adjust(left=0.035, right=0.965, bottom=0.04, top=0.76, wspace=0.12)
    figure.suptitle("Synthetic LPTEM-like image | In-distribution test, movie 1, frame 5",
                    fontsize=10, y=0.95)
    panels = [
        ("Simulated input", frame, -0.05, 1.05),
        ("True mask", truth, 0, 1),
        ("Local mean", predictions["Local mean"], 0, 1),
        ("CNN", predictions["CNN"], 0, 1),
    ]
    for axis, (label, data, low, high) in zip(axes, panels):
        axis.imshow(data, cmap="gray", vmin=low, vmax=high, interpolation="nearest")
        axis.set_title(label)
        axis.set_axis_off()
    figure.canvas.draw()
    # The four square image areas share physical widths, heights and repeated gutters.
    rectangles = np.array([axis.get_position().bounds for axis in axes])
    gaps = rectangles[1:, 0] - rectangles[:-1, 0] - rectangles[:-1, 2]
    if not (np.allclose(rectangles[:, 1:], rectangles[0, 1:]) and np.allclose(gaps, gaps[0])):
        raise RuntimeError("Image-panel alignment check failed")
    # Optional maintainer audit, kept separate from the student dependencies.
    try:
        from audit_panel_alignment import require_matplotlib_panel_alignment
    except ModuleNotFoundError:
        pass
    else:
        require_matplotlib_panel_alignment(figure, strict=True)
    figure.savefig(output / "ch07_lptem_example.svg")
    figure.savefig(output / "ch07_lptem_example.pdf")
    figure.savefig(output / "ch07_lptem_example.png", dpi=300)
    plt.close(figure)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--out", type=Path, default=Path("lptem_results"))
    parser.add_argument("--plot", action="store_true", help="Export figure with Matplotlib")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    train_rng, val_rng, test_rng, shifted_rng, model_rng = [
        np.random.default_rng(child) for child in np.random.SeedSequence(args.seed).spawn(5)
    ]
    train, train_truth = simulate(train_rng, 16)
    val, val_truth = simulate(val_rng, 4)
    parameters, history = train_cnn(local_patches(train), train_truth, model_rng)
    thresholds = {name: choose_threshold(score, val_truth)
                  for name, score in scores(val, parameters).items()}
    print(f"Seed {args.seed}; 16 train / 4 validation / 8 + 8 test movies")
    print(f"Weighted training BCE: {history[0][1]:.4f} -> {history[-1][1]:.4f}")
    with (args.out / "training.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(["epoch", "weighted_bce"])
        writer.writerows(history)
    with (args.out / "metrics.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(["condition", "method", "threshold", "movie", "iou", "dice",
                         "foreground_area_mae_px2"])
        for condition, rng, shifted in [("in_distribution", test_rng, False),
                                         ("shifted", shifted_rng, True)]:
            images, truth = simulate(rng, 8, shifted)
            predictions = {}
            for name, score in scores(images, parameters).items():
                predictions[name] = score >= thresholds[name]
                iou, dice, mae = evaluate(predictions[name], truth)
                for movie, metrics in enumerate(zip(iou, dice, mae), start=1):
                    writer.writerow([condition, name, thresholds[name], movie, *metrics])
                print(f"{condition:>15} | {name:>10} | IoU {iou.mean():.3f} | "
                      f"Dice {dice.mean():.3f} | area MAE {mae.mean():.1f} px^2")
            if args.plot and not shifted:
                plot_example(args.out, images[0, 4], truth[0, 4],
                             {name: mask[0, 4] for name, mask in predictions.items()})


if __name__ == "__main__":
    main()
