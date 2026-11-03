"""Compare four classifiers on grouped synthetic spectra (CPU)."""

import argparse
import csv
import json
from pathlib import Path

import numpy as np
import torch
from torch import nn


LENGTH = 64
CLASSES = 3
BATCHES = {"train": (0, 1, 2, 3, 4, 5), "validation": (6, 7), "test": (8, 9, 10, 11)}


def simulate(batches, data_seed):
    """Make 24 independent samples per batch and two scans per sample."""
    rows, labels, groups, sample_ids = [], [], [], []
    axis = np.linspace(0, 1, LENGTH)
    for batch in batches:
        rng = np.random.default_rng([data_seed, batch])
        shifted = batch >= 10
        baseline = rng.uniform(-0.22, 0.22) + (0.32 if shifted else 0)
        slope = rng.uniform(-0.20, 0.20) + (0.22 if shifted else 0)
        drift = rng.uniform(-0.014, 0.014) + (0.032 if shifted else 0)
        noise = 0.105 if shifted else 0.065
        for sample, label in enumerate(rng.permutation(np.repeat(np.arange(CLASSES), 8))):
            primary = (0.25, 0.34, 0.43)[label] + drift + rng.normal(0, 0.020)
            secondary = (0.68, 0.79, 0.71)[label] + drift + rng.normal(0, 0.029)
            a, b = rng.uniform(0.32, 0.85, size=2)
            width = rng.uniform(0.022, 0.048)
            signal = a * np.exp(-0.5 * ((axis - primary) / width) ** 2)
            signal += b * np.exp(-0.5 * ((axis - secondary) / 0.045) ** 2)
            signal += baseline + slope * axis
            for _ in range(2):
                rows.append(signal + rng.normal(0, noise, LENGTH))
                labels.append(label)
                groups.append(batch)
                sample_ids.append(batch * 24 + sample)
    return (
        torch.tensor(np.array(rows), dtype=torch.float32),
        torch.tensor(labels, dtype=torch.long),
        np.array(groups),
        np.array(sample_ids),
    )


class SpectralTransformer(nn.Module):
    """Encode ordered blocks of four intensities as 16 tokens."""

    def __init__(self):
        super().__init__()
        self.embed = nn.Linear(4, 16)
        self.position = nn.Parameter(torch.empty(1, LENGTH // 4, 16))
        nn.init.normal_(self.position, std=0.1)
        self.encoder = nn.TransformerEncoderLayer(
            d_model=16, nhead=4, dim_feedforward=32, dropout=0, batch_first=True
        )
        self.head = nn.Linear(LENGTH // 4 * 16, CLASSES)

    def forward(self, x):
        tokens = self.embed(x.reshape(x.shape[0], LENGTH // 4, 4))
        return self.head(self.encoder(tokens + self.position).flatten(1))


def models():
    return {
        "logistic": nn.Linear(LENGTH, CLASSES),
        "mlp": nn.Sequential(nn.Linear(LENGTH, 32), nn.ReLU(), nn.Linear(32, CLASSES)),
        "cnn": nn.Sequential(
            nn.Unflatten(1, (1, LENGTH)),
            nn.Conv1d(1, 12, 5, padding=2),
            nn.ReLU(),
            nn.Conv1d(12, 16, 5, padding=2),
            nn.ReLU(),
            nn.AvgPool1d(4),
            nn.Flatten(),
            nn.Linear(16 * (LENGTH // 4), CLASSES),
        ),
        "transformer": SpectralTransformer(),
    }


def metrics(y, predicted):
    matrix = np.zeros((CLASSES, CLASSES), dtype=int)
    np.add.at(matrix, (y, predicted), 1)
    denom = matrix.sum(axis=0) + matrix.sum(axis=1)
    f1 = np.divide(2 * matrix.diagonal(), denom, out=np.zeros(CLASSES), where=denom > 0)
    return {
        "accuracy": float(np.mean(y == predicted)),
        "macro_f1": float(f1.mean()),
        "confusion_matrix": matrix.tolist(),
    }


def evaluate(model, data):
    """Average scan probabilities, then score one prediction per sample."""
    model.eval()
    x, y, batch, ids = data
    with torch.no_grad():
        probability = model(x).softmax(dim=1).numpy()
    _, first, inverse, counts = np.unique(ids, return_index=True, return_inverse=True, return_counts=True)
    averaged = np.zeros((len(first), CLASSES))
    np.add.at(averaged, inverse, probability)
    averaged /= counts[:, None]
    return y.numpy()[first], averaged, batch[first], ids[first]


def fit(model, train, validation, epochs, seed):
    x, y, _, _ = train
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.003)
    shuffle = torch.Generator().manual_seed(seed)
    history, best = [], None
    for epoch in range(1, epochs + 1):
        model.train()
        loss_sum = 0.0
        for rows in torch.randperm(len(x), generator=shuffle).split(32):
            optimizer.zero_grad()
            loss = criterion(model(x[rows]), y[rows])
            loss.backward()
            optimizer.step()
            loss_sum += loss.item() * len(rows)
        val_y, val_p, _, _ = evaluate(model, validation)
        validation_nll = float(-np.log(np.clip(val_p[np.arange(len(val_y)), val_y], 1e-12, 1)).mean())
        history.append((epoch, loss_sum / len(x), validation_nll))
        if best is None or validation_nll < best[0]:
            best = (validation_nll, epoch, {name: value.clone() for name, value in model.state_dict().items()})
    model.load_state_dict(best[2])
    return best[1], history


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--seeds", type=int, nargs="+", default=[7, 19, 42])
    args = parser.parse_args()
    if args.epochs < 1 or len(set(args.seeds)) != len(args.seeds):
        parser.error("Use at least one epoch and distinct model seeds.")
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)

    data_seed = 2026
    data = {part: simulate(batches, data_seed) for part, batches in BATCHES.items()}
    train_x = data["train"][0]
    mean, std = train_x.mean(), train_x.std(unbiased=False).clamp_min(1e-8)
    data = {part: ((x - mean) / std, y, batch, ids) for part, (x, y, batch, ids) in data.items()}
    assert sum(map(len, BATCHES.values())) == len(set().union(*BATCHES.values()))

    args.out.mkdir(parents=True, exist_ok=True)
    records, learning, predictions = [], [], []
    for seed in args.seeds:
        torch.manual_seed(seed)
        for name, model in models().items():
            best_epoch, history = fit(model, data["train"], data["validation"], args.epochs, seed)
            learning.extend((name, seed, *row) for row in history)
            y, probability, batch, ids = evaluate(model, data["test"])
            predicted = probability.argmax(axis=1)
            predictions.extend(
                (name, seed, int(group), int(sample), int(actual), int(guess), *map(float, p))
                for group, sample, actual, guess, p in zip(batch, ids, y, predicted, probability)
            )
            subsets = {"all": np.ones(len(y), dtype=bool), "nominal": batch < 10, "shifted": batch >= 10}
            subsets.update({f"batch_{group}": batch == group for group in np.unique(batch)})
            report = {key: metrics(y[mask], predicted[mask]) for key, mask in subsets.items()}
            records.append({
                "model": name, "seed": seed, "epoch": best_epoch,
                "parameters": sum(p.numel() for p in model.parameters()), "test": report,
            })
            print(f"{name:12s} seed={seed:2d} epoch={best_epoch:2d} "
                  f"F1={report['all']['macro_f1']:.3f} shifted={report['shifted']['macro_f1']:.3f}")
    (args.out / "metrics.json").write_text(
        json.dumps({"data_seed": data_seed, "batches": BATCHES, "runs": records}, indent=2),
        encoding="utf-8",
    )
    for filename, header, rows in (
        ("history.csv", ("model", "seed", "epoch", "train_scan_nll", "validation_sample_nll"), learning),
        ("predictions.csv", ("model", "seed", "batch", "sample", "actual", "predicted", "p0", "p1", "p2"), predictions),
    ):
        with (args.out / filename).open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream)
            writer.writerow(header)
            writer.writerows(rows)


if __name__ == "__main__":
    main()
