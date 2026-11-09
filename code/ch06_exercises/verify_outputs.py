"""用标准库复核保存的第六章计算证据；不重新训练，不需要RDKit。"""
import argparse
import csv
import hashlib
import json
import math
import statistics
from collections import defaultdict
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read_csv(file):
    with file.open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))


def close(a, b):
    assert math.isclose(float(a), float(b), rel_tol=1e-9, abs_tol=1e-9), (a, b)


def verify(results, data):
    mols = read_csv(results / 'descriptors.csv')
    by_name = {r['name']: r for r in mols}
    assert len(mols) == 6
    close(by_name['ethanol']['MW_g_mol'], by_name['dimethyl_ether']['MW_g_mol'])
    assert (int(by_name['ethanol']['HBD']), int(by_name['dimethyl_ether']['HBD'])) == (1, 0)
    fps = read_csv(results / 'fingerprint_comparisons.csv')
    for a in ['E_2_butene', 'lactic_A']:
        pair = [r for r in fps if r['molecule_A'] == a]
        assert len(pair) == 2
        close(next(r['Tanimoto_binary'] for r in pair if r['includeChirality'] == 'False'), 1)
        assert float(next(r['Tanimoto_binary'] for r in pair if r['includeChirality'] == 'True')) < 1

    base = results / 'esol'
    manifest = json.loads((base / 'run_manifest.json').read_text(encoding='utf-8'))
    assert hashlib.sha256(data.read_bytes()).hexdigest() == manifest['sha256']
    raw = read_csv(data)
    clean = read_csv(base / 'cleaned_data.csv')
    duplicates = read_csv(base / 'duplicate_audit.csv')
    assert len(raw) == manifest['raw_rows'] == 1128
    assert len(clean) == manifest['kept_rows'] == 1117
    assert len(duplicates) == manifest['duplicates_removed'] == 11
    assert len({r['canonical_smiles'] for r in clean}) == len(clean)
    identities = {r['id']: r for r in clean}
    groups = defaultdict(list)
    for row in read_csv(base / 'split_assignments.csv'):
        groups[(row['split'], row['seed'])].append(row)
    assert len(groups) == 6
    test_ids = {}
    train_ids = {}
    for key, rows in groups.items():
        assert all(r['scaffold'] == identities[r['id']]['scaffold'] for r in rows)
        train = {r['id'] for r in rows if r['subset'] == 'train'}
        test = {r['id'] for r in rows if r['subset'] == 'test'}
        assert len(rows) == len(clean) and train | test == set(identities) and not train & test
        a = {identities[i]['canonical_smiles'] for i in train}
        b = {identities[i]['canonical_smiles'] for i in test}
        assert not a & b
        if key[0] == 'scaffold':
            assert not {identities[i]['scaffold'] for i in train} & {identities[i]['scaffold'] for i in test}
            assert len({r['subset'] for r in rows if r['scaffold'] == '__ACYCLIC__'}) == 1
        train_ids[key], test_ids[key] = train, test

    composition = read_csv(base / 'split_composition.csv')
    assert len(composition) == len(groups)
    representative_seeds = {}
    for row in composition:
        method, seed = row['split'], row['seed']
        test = test_ids[(method, seed)]
        representative = min(s for m, s in test_ids if m == method and test_ids[(m, s)] == test)
        assert row['representative_seed'] == representative
        n_acyclic = sum(identities[i]['scaffold'] == '__ACYCLIC__' for i in test)
        assert int(row['n_test']) == len(test)
        assert int(row['n_acyclic']) == n_acyclic
        assert int(row['n_cyclic']) == len(test) - n_acyclic
        representative_seeds[(method, seed)] = representative
    assert set(representative_seeds) == set(groups)
    distinct_counts = {method: len({frozenset(ids) for (m, _), ids in test_ids.items() if m == method})
                       for method in ('random', 'scaffold')}
    assert distinct_counts == {'random': 3, 'scaffold': 2}
    assert test_ids[('scaffold', '42')] == test_ids[('scaffold', '44')]

    fitted = json.loads((base / 'ridge_parameters.json').read_text(encoding='utf-8'))
    parameters = {}
    for record in fitted:
        key = (record['split'], str(record['seed']))
        assert set(record['train_ids']) == train_ids[key]
        for j, feature in enumerate(manifest['features']):
            values = [float(identities[i][feature]) for i in record['train_ids']]
            close(statistics.mean(values), record['mean'][j])
            close(statistics.pstdev(values) or 1, record['scale'][j])
        parameters[key] = record

    predictions = read_csv(base / 'predictions.csv')
    predicted = defaultdict(list)
    for row in predictions:
        key = (row['split'], row['seed'])
        assert row['id'] in test_ids[key]
        item = identities[row['id']]
        assert row['canonical_smiles'] == item['canonical_smiles']
        close(row['measured_logS'], item['target'])
        assert 0 <= float(row['nearest_train_tanimoto']) <= 1
        assert math.isfinite(float(row['predicted_logS']))
        close(abs(float(row['predicted_logS']) - float(row['measured_logS'])), row['absolute_error'])
        if row['model'] == 'training_mean':
            close(row['predicted_logS'], statistics.mean(float(identities[i]['target']) for i in train_ids[key]))
        elif row['model'] == 'descriptors_ridge':
            p = parameters[key]
            value = p['weights'][0] + sum((float(item[f]) - p['mean'][j]) / p['scale'][j] * p['weights'][j + 1]
                                             for j, f in enumerate(manifest['features']))
            close(value, row['predicted_logS'])
        predicted[(*key, row['model'])].append(row)
    metrics = read_csv(base / 'metrics.csv')
    assert len(metrics) == len(predicted) == 18
    for metric in metrics:
        key = (metric['split'], metric['seed'])
        rows = predicted[(*key, metric['model'])]
        assert len(rows) == len(test_ids[key]) == int(metric['n_test'])
        assert {r['id'] for r in rows} == test_ids[key]
        assert len(train_ids[key]) == int(metric['n_train'])
        close(statistics.mean(float(r['absolute_error']) for r in rows), metric['MAE_logS'])
        close(math.sqrt(statistics.mean(float(r['absolute_error']) ** 2 for r in rows)), metric['RMSE_logS'])

    knn = {key: {r['id']: float(r['predicted_logS']) for r in predicted[(*key, 'morgan_5nn')]}
           for key in groups}
    for left, right in combinations(groups, 2):
        if train_ids[left] == train_ids[right]:
            for identity in knn[left].keys() & knn[right].keys():
                assert knn[left][identity] == knn[right][identity], (left, right, identity)

    similarity_strata = {(r['split'], r['seed'], r['model'], r['stratum']): r
                         for r in read_csv(base / 'stratified_metrics.csv')
                         if r['stratum'].startswith('nearest_T_')}
    for key, rows in predicted.items():
        for name, members in (
            ('nearest_T_le_0.4', [r for r in rows if float(r['nearest_train_tanimoto']) <= .40]),
            ('nearest_T_gt_0.4', [r for r in rows if float(r['nearest_train_tanimoto']) > .40]),
        ):
            if members:
                stratum = similarity_strata.pop((*key, name))
                errors = [float(r['absolute_error']) for r in members]
                assert int(stratum['n']) == len(errors)
                close(statistics.mean(errors), stratum['MAE_logS'])
                close(math.sqrt(statistics.mean(e * e for e in errors)), stratum['RMSE_logS'])
    assert not similarity_strata

    for summary in read_csv(base / 'summary.csv'):
        rows = [m for m in metrics if m['split'] == summary['split'] and m['model'] == summary['model']]
        assert len(rows) == int(summary['n_seeds']) == 3
        rows = [m for m in rows if m['seed'] == representative_seeds[(m['split'], m['seed'])]]
        assert len(rows) == int(summary['n_distinct_splits']) == distinct_counts[summary['split']]
        for quantity in ['MAE', 'RMSE']:
            values = [float(r[quantity + '_logS']) for r in rows]
            close(statistics.mean(values), summary[quantity + '_mean'])
            close(statistics.stdev(values), summary[quantity + '_sd'])
    print(json.dumps({'molecules': len(mols), 'raw_rows': len(raw), 'clean_rows': len(clean),
                      'split_configurations': len(groups), 'distinct_splits': sum(distinct_counts.values()),
                      'distinct_splits_by_method': distinct_counts,
                      'metric_groups': len(metrics), 'predictions': len(predictions),
                      'checks': 'source hash; split composition and isolation; train-only scaling; tied kNN predictions; similarity strata; metrics: passed'}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--results', type=Path, default=ROOT / 'resources/annual/2026-2027/results/ch06')
    parser.add_argument('--data', type=Path, default=ROOT / 'data/ch06/delaney-processed.csv')
    args = parser.parse_args()
    verify(args.results, args.data)
