"""Regression tests: corrupt temporary copies of the published archive, never originals."""

import csv
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from verify_results import DEFAULT_ARCHIVE, verify


class ArchivedResultsTests(unittest.TestCase):
    def setUp(self):
        # Keep isolated copies inside the checkout; some Windows sandboxes deny the OS temp path.
        self.temp = tempfile.TemporaryDirectory(prefix="ch07-verify-test-", dir=Path(__file__).resolve().parents[2])
        self.addCleanup(self.temp.cleanup)
        self.archive = Path(self.temp.name) / "ch07"
        shutil.copytree(DEFAULT_ARCHIVE, self.archive)

    def edit_csv(self, name, edit):
        path = self.archive / name
        with path.open(encoding="utf-8", newline="") as stream:
            reader = csv.DictReader(stream)
            fields, rows = reader.fieldnames, list(reader)
        edit(rows)
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    def edit_json(self, name, edit):
        path = self.archive / name
        value = json.loads(path.read_text(encoding="utf-8"))
        edit(value)
        path.write_text(json.dumps(value), encoding="utf-8")

    def rejects_semantically(self, message):
        # Deliberately bypass checksums: the record checks must catch the defect independently.
        with self.assertRaisesRegex(ValueError, message):
            verify(self.archive, check_hashes=False)

    def test_default_archive_passes(self):
        result = verify(self.archive)
        self.assertEqual(result["record_counts"]["spectra_predictions"], 1152)

    def test_missing_prediction_fails_without_hash_check(self):
        self.edit_csv("spectra/predictions.csv", lambda rows: rows.pop())
        self.rejects_semantically("1152")

    def test_duplicate_prediction_with_unchanged_row_count_fails(self):
        self.edit_csv("spectra/predictions.csv", lambda rows: rows.__setitem__(1, dict(rows[0])))
        self.rejects_semantically("duplicate sample")

    def test_probability_argmax_mismatch_fails(self):
        self.edit_csv("spectra/predictions.csv", lambda rows: rows[0].update(predicted="0"))
        self.rejects_semantically("argmax")

    def test_probabilities_must_sum_to_one(self):
        self.edit_csv("spectra/predictions.csv", lambda rows: rows[0].update(p0="0.5"))
        self.rejects_semantically("sum to one")

    def test_cross_run_label_mismatch_fails(self):
        def change(rows):
            for row in rows:
                if row["model"] == "mlp" and row["sample"] == "192":
                    row["actual"] = "0"
                    return
        self.edit_csv("spectra/predictions.csv", change)
        self.rejects_semantically("inconsistent sample")

    def test_reported_confusion_matrix_mismatch_fails(self):
        self.edit_json("spectra/metrics.json",
                       lambda obj: obj["runs"][0]["test"]["all"]["confusion_matrix"][0].__setitem__(0, 999))
        self.rejects_semantically("confusion_matrix")

    def test_selected_epoch_mismatch_fails(self):
        self.edit_json("spectra/metrics.json", lambda obj: obj["runs"][0].update(epoch=1))
        self.rejects_semantically("selected epoch")

    def test_duplicate_lptem_movie_with_unchanged_row_count_fails(self):
        self.edit_csv("lptem/metrics.csv", lambda rows: rows.__setitem__(1, dict(rows[0])))
        self.rejects_semantically("duplicate/unexpected movie")

    def test_missing_lptem_training_epoch_fails(self):
        self.edit_csv("lptem/training.csv", lambda rows: rows.pop())
        self.rejects_semantically("20 training epochs")

    def test_summary_mismatch_fails_without_hash_check(self):
        self.edit_json("summary.json", lambda obj: obj["lptem"]["shifted/CNN"].update(iou=0.9))
        self.rejects_semantically("summary.json")

    def test_hash_mismatch_fails_for_semantically_identical_bytes(self):
        path = self.archive / "summary.json"
        path.write_text(path.read_text(encoding="utf-8") + "\n", encoding="utf-8")
        verify(self.archive, check_hashes=False)
        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
            verify(self.archive)


if __name__ == "__main__":
    unittest.main()
