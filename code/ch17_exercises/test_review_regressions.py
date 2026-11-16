"""Directed regression checks for G07 review; simulated hardware only."""
from pathlib import Path
import importlib.util
import unittest
from unittest.mock import patch

import numpy as np

HERE = Path(__file__).resolve().parent

def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

rl = load('reward', '02_reward_and_shield.py')
fsm = load('fsm', '03_fsm_fault_injection.py')

class ScriptedHardware(fsm.Hardware):
    """No random faults; use separately scripted sample and reference replies."""
    reference = []
    sample_timeouts = False
    instances = []

    def __init__(self, rng):
        super().__init__(rng)
        self.reference_calls = self.sample_calls = self.calibrations = 0
        self.__class__.instances.append(self)

    def fault(self, name):
        return False

    def measure(self, true_a):
        if true_a == 0.5:
            self.reference_calls += 1
            # A hard guard exposes a regression without hanging the test runner.
            if self.reference_calls > 12:
                raise AssertionError('Reference retry loop did not terminate')
            index = min(self.reference_calls - 1, len(self.reference) - 1)
            return self.reference[index] if self.reference else 0.5
        self.sample_calls += 1
        if self.sample_calls > 12:
            raise AssertionError('Sample retry loop did not terminate')
        return None if self.sample_timeouts else true_a

    def recalibrate(self):
        self.calibrations += 1
        super().recalibrate()

class ReviewRegressionTests(unittest.TestCase):
    def hardware_run(self, reference, sample_timeouts=False):
        class CaseHardware(ScriptedHardware):
            pass
        CaseHardware.reference = reference
        CaseHardware.sample_timeouts = sample_timeouts
        CaseHardware.instances = []
        with patch.object(fsm, 'Hardware', CaseHardware):
            stats, log = fsm.run('robust', n_samples=1)
        return stats, log, CaseHardware.instances[0]

    def test_persistent_reference_timeout_stops_and_requests_human(self):
        stats, log, hw = self.hardware_run([None])
        self.assertEqual(hw.reference_calls, fsm.MAX_RETRY + 1)
        self.assertEqual(hw.sample_calls, 1)
        self.assertEqual((stats['safe'], stats['human'], stats['flagged']), (1, 1, 1))
        self.assertEqual(stats['valid'] + stats['silent_wrong'], 0)
        self.assertTrue(any('参比通信连续超时' in msg for _, msg in log))
        # Each of the three failed reference calls incurs its one-minute wait.
        baseline, _, _ = self.hardware_run([0.5])
        self.assertAlmostEqual(stats['minutes'] - baseline['minutes'], 19.0)

    def test_reference_communication_can_recover(self):
        stats, log, hw = self.hardware_run([None, 0.5])
        self.assertEqual(hw.reference_calls, 2)
        self.assertEqual((stats['valid'], stats['human']), (1, 0))
        self.assertEqual(log, [])

    def test_reference_communication_does_not_spend_recalibration_budget(self):
        stats, log, hw = self.hardware_run([None, 0.6, None, 0.6, None, 0.5])
        self.assertEqual((hw.reference_calls, hw.calibrations), (6, 2))
        self.assertEqual((stats['valid'], stats['safe']), (1, 0))
        self.assertEqual(log, [])

    def test_persistent_qc_failure_has_separate_finite_limit(self):
        stats, log, hw = self.hardware_run([0.6])
        self.assertEqual((hw.reference_calls, hw.calibrations), (3, 2))
        self.assertEqual((stats['safe'], stats['human']), (1, 1))
        self.assertTrue(any('参比质控持续不合格' in msg for _, msg in log))

    def test_sample_timeout_still_stops(self):
        stats, log, hw = self.hardware_run([], sample_timeouts=True)
        self.assertEqual((hw.sample_calls, hw.reference_calls), (3, 0))
        self.assertEqual((stats['safe'], stats['human']), (1, 1))
        self.assertTrue(any('光谱仪连续超时' in msg for _, msg in log))

    def well_at_350(self):
        env = rl.ColorimetricWell(np.random.default_rng(1))
        env.reset()
        env.adds, env.dils = 3, 1
        self.assertEqual(env.volume, 350)
        return env

    def test_backup_ignores_high_illegal_action_value(self):
        env = self.well_at_350()
        values = np.full(len(rl.ACTIONS), -0.02)
        values[rl.ACTIONS.index('稀释')] = 1000.0
        self.assertAlmostEqual(rl.backup_target(env, values, -0.3, False, True), -0.3196)
        values[rl.ACTIONS.index('稀释')] = 0.0
        self.assertAlmostEqual(rl.backup_target(env, values, -0.3, False, True), -0.3196)
        self.assertAlmostEqual(rl.backup_target(env, values, -0.3, False, False), -0.3)

    def test_terminal_backup_never_bootstraps(self):
        self.assertEqual(rl.backup_target(None, None, -20.0, True, True), -20.0)

    def test_b_and_c_have_same_environment_capacity(self):
        for label in ('B', 'C'):
            with self.subTest(setting=label):
                env = self.well_at_350()
                self.assertFalse(rl.shield(env, '稀释'))
                _, reward, done, info = env.step('稀释')
                self.assertEqual((reward, done, info.get('overflow')), (-20.0, True, True))

if __name__ == '__main__':
    unittest.main(verbosity=2)
