"""Independently recompute the primary metrics from CSV and check source records."""

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'data/ch15'
RESULTS = ROOT / 'resources/annual/2026-2027/results/ch15'
KNOWN_LABELS = ('Carbonate', 'Sulphate', 'Phosphate')
UNKNOWN_SOURCE_LABEL = 'Si_O_without_target_anions'
EXPECTED_SEEDS = [2026102901, 2026102902, 2026102903, 2026102904, 2026102905]
SAMPLE_COUNT = 280


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_csv(path):
    with path.open(encoding='utf-8-sig', newline='') as file:
        return list(csv.DictReader(file))


def index_by_id(records, filename):
    index = {}
    for rruff_id, record in records:
        require(rruff_id not in index, f'{filename}: duplicate RRUFF ID {rruff_id}')
        index[rruff_id] = record
    return index


def verify_sample_records(data_dir, rows):
    manifest = read_csv(data_dir / 'sample_manifest.csv')
    by_id = index_by_id(((row['rruff_id'], row) for row in manifest), 'sample_manifest.csv')
    predictions = index_by_id(((row['rruff_id'], row) for row in rows), 'predictions.csv')
    require(len(by_id) == SAMPLE_COUNT, f'sample_manifest.csv: expected {SAMPLE_COUNT} unique IDs')

    with np.load(data_dir / 'selected_spectra.npz', allow_pickle=False) as data:
        ids, labels, spectra = data['ids'], data['y'], data['X']
    require(ids.shape == labels.shape == (SAMPLE_COUNT,), 'selected_spectra.npz: invalid ids or y shape')
    require(spectra.shape == (SAMPLE_COUNT, 501), 'selected_spectra.npz: invalid X shape')
    spectral_rows = index_by_id(
        ((rruff_id, (label, spectrum)) for rruff_id, label, spectrum in zip(ids.tolist(), labels.tolist(), spectra)),
        'selected_spectra.npz',
    )

    for filename, index in [('selected_spectra.npz', spectral_rows), ('predictions.csv', predictions)]:
        missing = sorted(by_id.keys() - index.keys())
        extra = sorted(index.keys() - by_id.keys())
        require(not missing and not extra, f'{filename}: ID mismatch; missing={missing}, extra={extra}')

    spectrum_ids = {}
    for rruff_id, (npz_label, spectrum) in spectral_rows.items():
        sample = by_id[rruff_id]
        prediction = predictions[rruff_id]
        source_label = sample['class_label']
        require(npz_label == source_label, f'{rruff_id}: label mismatch: NPZ y={npz_label!r}, manifest class_label={source_label!r}')
        require(source_label in (*KNOWN_LABELS, UNKNOWN_SOURCE_LABEL), f'{rruff_id}: unsupported source label {source_label!r}')
        is_unknown = source_label == UNKNOWN_SOURCE_LABEL
        expected_label = 'unknown' if is_unknown else source_label
        actual_label = prediction['true_label']
        require(actual_label == expected_label, f'{rruff_id}: label mismatch: predictions true_label={actual_label!r}, expected {expected_label!r}')
        require((prediction['role'] == 'unknown_test') == is_unknown, f'{rruff_id}: label and unknown_test role disagree')
        require(np.isfinite(spectrum).all(), f'{rruff_id}: non-finite spectrum')
        fingerprint = hashlib.sha256(spectrum.astype('<f8').tobytes()).hexdigest()
        require(fingerprint == sample['spectrum_sha256'], f'{rruff_id}: spectrum SHA-256 mismatch between NPZ and manifest')
        if fingerprint in spectrum_ids:
            raise ValueError(f'{rruff_id}: duplicate spectrum of {spectrum_ids[fingerprint]}')
        spectrum_ids[fingerprint] = rruff_id

    excluded = {row['rruff_id'] for row in read_csv(data_dir / 'pilot_excluded_ids.csv')}
    require(len(excluded) == 340, 'pilot_excluded_ids.csv: expected 340 unique IDs')
    overlap = sorted(by_id.keys() & excluded)
    require(not overlap, f'Pilot IDs overlap with the experiment: {overlap}')


def verify_seed_scope(metrics, primary_only):
    expected = EXPECTED_SEEDS[:1] if primary_only else EXPECTED_SEEDS
    mode = 'primary-only' if primary_only else 'full'
    recorded = [row.get('seed') for row in metrics.get('sensitivity_runs', [])]
    if recorded != expected:
        hint = ''
        if not primary_only and recorded == EXPECTED_SEEDS[:1]:
            hint = ' Use --primary-only to verify a primary-only run.'
        raise ValueError(f'{mode} mode expects seed records {expected}; found {recorded}.{hint}')
    require(metrics.get('seed') == EXPECTED_SEEDS[0], f'Expected primary seed {EXPECTED_SEEDS[0]} in metrics.json')
    return {'mode': mode, 'recorded_seeds': recorded, 'metrics_recomputed_seed': metrics['seed']}


def near(actual, expected):
    require(math.isclose(actual, expected, rel_tol=1e-10, abs_tol=1e-10),
            f'Numeric mismatch: recomputed {actual}, recorded {expected}')


def verify_rejection_counts(summary, known, unknown, score):
    threshold = summary['threshold']
    accepted_known = [row for row in known if score(row) <= threshold]
    accepted_unknown = [row for row in unknown if score(row) <= threshold]
    require(len(accepted_known) == summary['known_accepted'], 'Known acceptance count mismatch')
    require(len(accepted_unknown) == summary['unknown_accepted'], 'Unknown acceptance count mismatch')
    errors = sum(row['true_label'] != row['predicted_label'] for row in accepted_known)
    require(errors == summary['accepted_known_errors'], 'Accepted known error count mismatch')
    recorded_rate = summary['accepted_known_error_rate']
    if accepted_known:
        require(recorded_rate is not None, 'Expected an error rate for accepted known samples')
        near(errors / len(accepted_known), recorded_rate)
    else:
        require(recorded_rate is None, 'Expected null accepted_known_error_rate when no known samples are accepted')


def verify_results(results, primary_only=False):
    metrics = json.loads((results / 'metrics.json').read_text(encoding='utf-8'))
    seed_scope = verify_seed_scope(metrics, primary_only)
    rows = read_csv(results / 'predictions.csv')
    verify_sample_records(DATA, rows)
    for role, count in metrics['role_counts'].items():
        require(sum(row['role'] == role for row in rows) == count, f'Role count mismatch: {role}')

    known = [row for row in rows if row['role'] == 'known_test']
    unknown = [row for row in rows if row['role'] == 'unknown_test']
    require(len(known) == 36 and len(unknown) == 100, 'Expected 36 known and 100 unknown test samples')
    for row in rows:
        before = np.array([float(row[f'p_before_{k}']) for k in range(3)])
        after = np.array([float(row[f'p_after_{k}']) for k in range(3)])
        near(before.sum(), 1)
        near(after.sum(), 1)
        require(before.argmax() == after.argmax(), f"{row['rruff_id']}: temperature scaling changed argmax")
        expected = before ** (1 / metrics['temperature'])
        expected /= expected.sum()
        require(np.allclose(expected, after, atol=1e-12), f"{row['rruff_id']}: temperature relation mismatch")

    for prefix, key in [('p_before_', 'known_before'), ('p_after_', 'known_after')]:
        losses, brier, bins = [], [], [[] for _ in range(5)]
        correct = 0
        for row in known:
            label = KNOWN_LABELS.index(row['true_label'])
            probability = [float(row[f'{prefix}{k}']) for k in range(3)]
            confidence = max(probability)
            good = probability.index(confidence) == label
            correct += good
            losses.append(-math.log(probability[label]))
            brier.append(sum((value - (k == label)) ** 2 for k, value in enumerate(probability)))
            bins[min(4, int(confidence * 5))].append((confidence, good))
        ece = sum(abs(sum(c for c, g in group) - sum(g for c, g in group)) for group in bins if group) / len(known)
        near(correct / len(known), metrics[key]['accuracy'])
        near(sum(losses) / len(known), metrics[key]['nll'])
        near(sum(brier) / len(known), metrics[key]['brier'])
        near(ece, metrics[key]['ece_5_equal_bins'])

    scores = [
        ('tq_rejection', lambda row: float(row['ad_score'])),
        ('msp_reference', lambda row: 1 - float(row['confidence_after'])),
    ]
    for key, score in scores:
        summary = metrics[key]
        verify_rejection_counts(summary, known, unknown, score)
        pairs = ((score(u), score(k)) for u in unknown for k in known)
        auc = sum((u > k) + .5 * (u == k) for u, k in pairs) / (len(unknown) * len(known))
        near(auc, summary['unknown_positive_auroc'])
        validation_scores = sorted(score(row) for row in rows if row['role'] == 'threshold_validation')
        near(validation_scores[math.ceil(.9 * (len(validation_scores) - 1))], summary['threshold'])

    return {
        'status': 'passed',
        'rows': len(rows),
        'known_final_test': len(known),
        'unknown_final_test': len(unknown),
        'pilot_overlap': 0,
        'seed_verification': seed_scope,
        'checks': [
            'primary CSV metrics independently recomputed',
            'probabilities normalized',
            'temperature relation and argmax',
            'rejection counts and conditional error rate',
            'pairwise AUROC',
            'validation-only threshold quantiles',
            'role counts and unique groups',
            'per-ID NPZ, manifest and prediction labels',
            'finite spectra, per-ID SHA-256 and exact duplicates',
            'sensitivity seed records in the selected mode',
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--results', type=Path, default=RESULTS)
    parser.add_argument('--primary-only', action='store_true',
                        help='Verify output generated by run_case.py --primary-only')
    args = parser.parse_args()
    try:
        report = verify_results(args.results, primary_only=args.primary_only)
    except ValueError as error:
        parser.exit(1, f'Verification failed: {error}\n')
    (args.results / 'verification.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8'
    )
    print(json.dumps(report, ensure_ascii=False))


if __name__ == '__main__':
    main()
