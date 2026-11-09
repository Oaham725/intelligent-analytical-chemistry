"""Regression checks for the cases raised in the Chapter 15 review."""

import shutil
import tempfile
import unittest
from pathlib import Path

import numpy as np

from verify_results import (
    DATA,
    RESULTS,
    read_csv,
    verify_rejection_counts,
    verify_sample_records,
    verify_seed_scope,
)


class SampleRecordsTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.data = Path(temporary.name)
        for name in ('sample_manifest.csv', 'pilot_excluded_ids.csv'):
            shutil.copyfile(DATA / name, self.data / name)
        with np.load(DATA / 'selected_spectra.npz', allow_pickle=False) as source:
            self.arrays = {name: source[name] for name in source.files}
        self.predictions = read_csv(RESULTS / 'predictions.csv')

    def verify_copy(self):
        np.savez_compressed(self.data / 'selected_spectra.npz', **self.arrays)
        verify_sample_records(self.data, self.predictions)

    def test_original_records_pass(self):
        self.verify_copy()

    def test_record_order_can_differ(self):
        for key in ('ids', 'y', 'X'):
            self.arrays[key] = self.arrays[key][::-1]
        self.verify_copy()

    def test_npz_label_change_reports_id(self):
        rruff_id = self.arrays['ids'][0]
        self.arrays['y'][0] = 'Phosphate'
        with self.assertRaisesRegex(ValueError, f'{rruff_id}: label mismatch'):
            self.verify_copy()

    def test_spectrum_swap_reports_id(self):
        rruff_id = self.arrays['ids'][0]
        self.arrays['X'][[0, 1]] = self.arrays['X'][[1, 0]]
        with self.assertRaisesRegex(ValueError, f'{rruff_id}: spectrum SHA-256 mismatch'):
            self.verify_copy()

    def test_unknown_prediction_requires_mapped_label(self):
        row = next(row for row in self.predictions if row['true_label'] == 'unknown')
        row['true_label'] = 'Si_O_without_target_anions'
        with self.assertRaisesRegex(ValueError, f"{row['rruff_id']}: label mismatch"):
            self.verify_copy()

    def test_duplicate_prediction_reports_id(self):
        self.predictions[1]['rruff_id'] = self.predictions[0]['rruff_id']
        with self.assertRaisesRegex(ValueError, f"duplicate RRUFF ID {self.predictions[0]['rruff_id']}"):
            self.verify_copy()


class SeedScopeTests(unittest.TestCase):
    seeds = [2026102901, 2026102902, 2026102903, 2026102904, 2026102905]

    def records(self, seeds):
        return {'seed': 2026102901, 'sensitivity_runs': [{'seed': seed} for seed in seeds]}

    def test_primary_scope_reports_only_primary_seed(self):
        metrics = self.records([2026102901])
        self.assertEqual(verify_seed_scope(metrics, primary_only=True), {
            'mode': 'primary-only', 'recorded_seeds': [2026102901], 'metrics_recomputed_seed': 2026102901,
        })
        with self.assertRaisesRegex(ValueError, 'Use --primary-only'):
            verify_seed_scope(metrics, primary_only=False)

    def test_full_scope_rejects_each_missing_seed(self):
        self.assertEqual(verify_seed_scope(self.records(self.seeds), primary_only=False)['recorded_seeds'], self.seeds)
        for missing in self.seeds:
            with self.subTest(missing=missing):
                records = self.records([seed for seed in self.seeds if seed != missing])
                with self.assertRaisesRegex(ValueError, 'full mode expects seed records'):
                    verify_seed_scope(records, primary_only=False)


class RejectionTests(unittest.TestCase):
    known = [
        {'score': .2, 'true_label': 'Carbonate', 'predicted_label': 'Phosphate'},
        {'score': .8, 'true_label': 'Sulphate', 'predicted_label': 'Sulphate'},
    ]
    unknown = [{'score': .1}, {'score': .9}]

    def verify_counts(self, threshold, known_count, unknown_count, errors, error_rate):
        summary = {
            'threshold': threshold,
            'known_accepted': known_count,
            'unknown_accepted': unknown_count,
            'accepted_known_errors': errors,
            'accepted_known_error_rate': error_rate,
        }
        verify_rejection_counts(summary, self.known, self.unknown, lambda row: row['score'])

    def test_partial_acceptance_includes_threshold_ties(self):
        self.verify_counts(.2, 1, 1, 1, 1.0)

    def test_all_accepted(self):
        self.verify_counts(.9, 2, 2, 1, .5)

    def test_empty_known_acceptance_requires_null_error_rate(self):
        self.verify_counts(.1, 0, 1, 0, None)
        with self.assertRaisesRegex(ValueError, 'Expected null accepted_known_error_rate'):
            self.verify_counts(.1, 0, 1, 0, 0.0)
        with self.assertRaisesRegex(ValueError, 'Accepted known error count mismatch'):
            self.verify_counts(.1, 0, 1, 1, None)


if __name__ == '__main__':
    unittest.main()
