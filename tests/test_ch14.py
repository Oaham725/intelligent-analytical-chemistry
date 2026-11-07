from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))

from ch14 import (  # noqa: E402
    PLS1,
    apply_global_ds,
    apply_pds,
    check_metadata,
    fit_global_ds,
    fit_pds,
    generate_case,
    regression_metrics,
    sha256_array,
)


class Chapter14Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.train, cls.transfer, cls.test, _ = generate_case(seed=42)
        cls.model = PLS1(n_components=9).fit(cls.train.x_master, cls.train.y)

    def test_pls_prediction_is_finite(self):
        prediction = self.model.predict(self.test.x_slave)
        self.assertEqual(prediction.shape, self.test.y.shape)
        self.assertTrue(np.isfinite(prediction).all())

    def test_ds_and_pds_map_to_master_space(self):
        transform, slave_mean, master_mean = fit_global_ds(
            self.transfer.x_slave, self.transfer.x_master
        )
        transformed = apply_global_ds(
            self.test.x_slave, transform, slave_mean, master_mean
        )
        self.assertEqual(transformed.shape, self.test.x_slave.shape)

        models = fit_pds(self.transfer.x_slave, self.transfer.x_master)
        transformed_pds = apply_pds(self.test.x_slave, models)
        self.assertEqual(transformed_pds.shape, self.test.x_slave.shape)
        self.assertTrue(np.isfinite(transformed_pds).all())

    def test_transfer_improves_over_direct_slave_use(self):
        direct = self.model.predict(self.test.x_slave)
        transform, slave_mean, master_mean = fit_global_ds(
            self.transfer.x_slave, self.transfer.x_master
        )
        pds_models = fit_pds(self.transfer.x_slave, self.transfer.x_master)
        pds = self.model.predict(apply_pds(self.test.x_slave, pds_models))
        ds = self.model.predict(
            apply_global_ds(self.test.x_slave, transform, slave_mean, master_mean)
        )
        direct_rmse = regression_metrics(self.test.y, direct)["rmsep"]
        ds_rmse = regression_metrics(self.test.y, ds)["rmsep"]
        pds_rmse = regression_metrics(self.test.y, pds)["rmsep"]
        self.assertLess(min(ds_rmse, pds_rmse), direct_rmse)

    def test_metadata_accepts_complete_record(self):
        record = {
            "sample_id": "S-001",
            "batch_id": "B-001",
            "instrument_id": "NIR-02",
            "acquired_at": "2026-10-31T12:00:00+08:00",
            "wavelength_start_nm": 1100.0,
            "wavelength_end_nm": 2400.0,
            "points": 160,
            "unit": "absorbance",
            "preprocess": "SNV",
            "sha256": sha256_array(np.array([1.0, 2.0])),
            "calibration_id": "CAL-001",
            "model_version": "1.0.0",
        }
        self.assertEqual(check_metadata(record), [])

    def test_metadata_rejects_missing_unit_and_bad_hash(self):
        record = {
            "sample_id": "S-001",
            "batch_id": "B-001",
            "instrument_id": "NIR-02",
            "acquired_at": "2026-10-31T12:00:00+08:00",
            "wavelength_start_nm": 1100.0,
            "wavelength_end_nm": 2400.0,
            "points": 160,
            "preprocess": "SNV",
            "sha256": "bad",
            "calibration_id": "CAL-001",
            "model_version": "1.0.0",
        }
        errors = check_metadata(record)
        self.assertTrue(any("unit" in error for error in errors))
        self.assertTrue(any("sha256" in error for error in errors))


if __name__ == "__main__":
    unittest.main()

