"""Run: python code/ch07_exercises/test_spectra_groups.py (NumPy and PyTorch)."""

import sys
import unittest
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ch07 import BATCHES, CLASSES, LENGTH, evaluate, simulate, validate_samples, validate_splits


class NoInference(torch.nn.Module):
    def forward(self, x):
        raise AssertionError("Invalid metadata must be rejected before inference.")


class FirstColumns(torch.nn.Module):
    def forward(self, x):
        return x[:, :CLASSES]


class SampleGroupingTests(unittest.TestCase):
    def setUp(self):
        self.data = {part: simulate(batches, 2026) for part, batches in BATCHES.items()}

    def test_default_protocol_counts(self):
        summary = validate_splits(self.data)
        self.assertEqual(
            {part: (r["samples"], r["scans"]) for part, r in summary.items()},
            {"train": (144, 288), "validation": (48, 96), "test": (96, 192)},
        )

    def test_conflicting_labels_fail_before_inference(self):
        x, y, batch, ids = self.data["test"]
        y[1] = (y[0] + 1) % CLASSES
        with self.assertRaisesRegex(ValueError, "conflicting labels"):
            evaluate(NoInference(), (x, y, batch, ids))

    def test_conflicting_batches_fail_before_inference(self):
        x, y, batch, ids = self.data["test"]
        batch[1] = batch[0] + 1
        with self.assertRaisesRegex(ValueError, "conflicting batch IDs"):
            evaluate(NoInference(), (x, y, batch, ids))

    def test_sample_overlap_fails_even_with_distinct_batches(self):
        # Both scans retain consistent metadata. Batch separation alone misses this.
        self.data["test"][3][:2] = self.data["train"][3][0]
        with self.assertRaisesRegex(ValueError, "train/test: overlapping sample IDs"):
            validate_splits(self.data)

    def test_all_partition_pairs_are_checked(self):
        self.data["test"][3][:2] = self.data["validation"][3][0]
        with self.assertRaisesRegex(ValueError, "validation/test: overlapping sample IDs"):
            validate_splits(self.data)

    def test_batch_overlap_fails_even_with_distinct_samples(self):
        self.data["test"][2][:2] = self.data["train"][2][0]
        with self.assertRaisesRegex(ValueError, "overlapping batch IDs"):
            validate_splits(self.data)

    def test_missing_scan_fails_default_protocol(self):
        self.data["test"] = tuple(field[1:] for field in self.data["test"])
        with self.assertRaisesRegex(ValueError, "has 1 scans; expected 2"):
            validate_splits(self.data)

    def test_extra_scan_fails_default_protocol(self):
        x, y, batch, ids = self.data["test"]
        self.data["test"] = (
            torch.cat((x, x[:1])), torch.cat((y, y[:1])),
            np.concatenate((batch, batch[:1])), np.concatenate((ids, ids[:1])),
        )
        with self.assertRaisesRegex(ValueError, "has 3 scans; expected 2"):
            validate_splits(self.data)

    def test_bad_shapes_and_lengths_fail(self):
        x, y, batch, ids = self.data["test"]
        cases = [
            ((x[:, :3], y, batch, ids), "spectra must have"),
            ((x, y[:-1], batch, ids), "different lengths"),
            ((x, y, batch[:, None], ids), "one-dimensional"),
        ]
        for values, message in cases:
            with self.subTest(message=message), self.assertRaisesRegex(ValueError, message):
                validate_samples(values)

    def test_average_probabilities_not_logits_and_preserve_metadata(self):
        x = torch.zeros(4, LENGTH)
        # Two samples interleaved and deliberately not sorted by ID.
        x[:, :3] = torch.tensor([[4., 0., 0.], [0., 1., 0.], [0., 0., 0.], [0., 3., 0.]])
        y, batch, ids = torch.tensor([0, 1, 0, 1]), np.array([9, 8, 9, 8]), np.array([11, 10, 11, 10])
        actual_y, actual_p, actual_batch, actual_ids = evaluate(FirstColumns(), (x, y, batch, ids))
        scan_p = torch.softmax(x[:, :3], dim=1).numpy()
        expected = np.stack((scan_p[[1, 3]].mean(axis=0), scan_p[[0, 2]].mean(axis=0)))
        np.testing.assert_allclose(actual_p, expected, atol=1e-7)
        np.testing.assert_array_equal(actual_y, [1, 0])
        np.testing.assert_array_equal(actual_batch, [8, 9])
        np.testing.assert_array_equal(actual_ids, [10, 11])
        averaged_logits = torch.stack((x[[1, 3], :3].mean(0), x[[0, 2], :3].mean(0)))
        self.assertFalse(np.allclose(actual_p, averaged_logits.softmax(1).numpy()))


if __name__ == "__main__":
    torch.set_num_threads(1)
    unittest.main(verbosity=2)
