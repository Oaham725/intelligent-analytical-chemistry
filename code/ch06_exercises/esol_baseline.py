"""第6章：ESOL真实数据的描述符与指纹基线，以及随机/骨架留出对照。

从仓库根目录运行：python code/ch06_exercises/esol_baseline.py --output results/esol
省略--data时，默认读取仓库内的data/ch06/delaney-processed.csv。
依赖：rdkit, numpy, matplotlib（仅画图）。参数预先固定，不使用测试集调参。
数据来源：https://github.com/deepchem/deepchem/blob/master/datasets/delaney-processed.csv
原始研究：Delaney, 2004, DOI 10.1021/ci034243x。
"""
import argparse
import csv
import hashlib
import json
import platform
from collections import defaultdict
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path

import numpy as np
from rdkit import Chem, DataStructs, rdBase
from rdkit.Chem import Descriptors, rdFingerprintGenerator
from rdkit.Chem.Scaffolds import MurckoScaffold

TARGET = 'measured log solubility in mols per litre'
FEATURES = ['MW_g_mol', 'HBD', 'HBA', 'TPSA_A2', 'MolLogP', 'RotatableBonds', 'AromaticAtomFraction']
SOURCE = 'https://github.com/deepchem/deepchem/blob/master/datasets/delaney-processed.csv'
SOURCE_BLOB = '970b0d32771f1d67175d4f4a630e13f446ba97a8'
SEEDS = (42, 43, 44)
MODELS = ('training_mean', 'descriptors_ridge', 'morgan_5nn')
LOW_SIMILARITY_MAX = 0.40


def write_csv(path, rows):
    if not rows:
        path.write_text('', encoding='utf-8')
        return
    with path.open('w', newline='', encoding='utf-8-sig') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def load_data(path):
    rows, rejected, duplicates, seen = [], [], [], {}
    with path.open(encoding='utf-8-sig', newline='') as stream:
        source_rows = list(csv.DictReader(stream))
    for line, source in enumerate(source_rows, start=2):
        mol = Chem.MolFromSmiles(source['smiles'])
        if mol is None:
            rejected.append({'line': line, 'smiles': source['smiles'], 'reason': 'parse_failed'})
            continue
        try:
            target = float(source[TARGET])
            if not np.isfinite(target):
                raise ValueError()
        except ValueError:
            rejected.append({'line': line, 'smiles': source['smiles'], 'reason': 'invalid_target'})
            continue
        identity = Chem.MolToSmiles(mol, isomericSmiles=True)
        if identity in seen:
            first = seen[identity]
            duplicates.append({'line': line, 'canonical_smiles': identity,
                               'first_id': first['id'], 'kept_logS': first['target'],
                               'excluded_logS': target, 'absolute_difference': abs(first['target'] - target),
                               'policy': 'keep_first_no_averaging'})
            continue
        core = MurckoScaffold.MurckoScaffoldSmiles(mol=mol, includeChirality=False)
        scaffold = core if core else '__ACYCLIC__'
        features = [Descriptors.MolWt(mol), Descriptors.NumHDonors(mol), Descriptors.NumHAcceptors(mol),
                    Descriptors.TPSA(mol), Descriptors.MolLogP(mol), Descriptors.NumRotatableBonds(mol),
                    sum(a.GetIsAromatic() for a in mol.GetAtoms()) / mol.GetNumAtoms()]
        row = {'id': f'ESOL-{line-1:04d}', 'source_line': line, 'name': source['Compound ID'],
               'canonical_smiles': identity, 'scaffold': scaffold, 'target': target,
               'features': features, 'mol': mol, 'n_heavy_atoms': mol.GetNumHeavyAtoms(),
               'formal_charge': Chem.GetFormalCharge(mol)}
        rows.append(row)
        seen[identity] = row
    return rows, source_rows, duplicates, rejected


def split_indices(rows, method, seed):
    rng = np.random.default_rng(seed)
    n = len(rows)
    if method == 'random':
        order = rng.permutation(n)
        cut = int(np.floor(n * .8))
        return order[:cut], order[cut:]
    groups = defaultdict(list)
    for i, row in enumerate(rows):
        groups[row['scaffold']].append(i)
    # 明确定义：所有无环分子作为一个组；整组分配，绝不拆散以凑比例。
    group_list = [groups[key] for key in sorted(groups)]
    order = rng.permutation(len(group_list))
    target_train = int(np.floor(n * .8))
    train, test = [], []
    for j in order:
        group = group_list[j]
        (train if len(train) + len(group) <= target_train else test).extend(group)
    assert train and test
    return np.array(train), np.array(test)


def ridge_fit_predict(x_train, y_train, x_test, alpha=1.0):
    # 标准化只拟合训练集。截距不惩罚，目标不做跨集合归一化。
    mean = x_train.mean(axis=0)
    scale = x_train.std(axis=0)
    scale[scale == 0] = 1
    a = np.column_stack([np.ones(len(x_train)), (x_train - mean) / scale])
    b = np.column_stack([np.ones(len(x_test)), (x_test - mean) / scale])
    penalty = np.eye(a.shape[1]) * alpha
    penalty[0, 0] = 0
    weights = np.linalg.solve(a.T @ a + penalty, a.T @ y_train)
    return b @ weights, {'mean': mean.tolist(), 'scale': scale.tolist(), 'weights': weights.tolist()}


def metrics(y, pred):
    return float(np.abs(pred - y).mean()), float(np.sqrt(np.mean((pred - y) ** 2)))


def run(args):
    out = args.output
    out.mkdir(parents=True, exist_ok=True)
    rows, raw, duplicates, rejected = load_data(args.data)
    write_csv(out / 'duplicate_audit.csv', duplicates)
    write_csv(out / 'rejected_records.csv', rejected)
    write_csv(out / 'cleaned_data.csv', [{k: row[k] for k in ['id', 'source_line', 'name', 'canonical_smiles', 'scaffold', 'target']}
              | dict(zip(FEATURES, row['features'])) for row in rows])
    x = np.array([r['features'] for r in rows], dtype=float)
    y = np.array([r['target'] for r in rows])
    assert np.isfinite(x).all() and np.isfinite(y).all()
    assert len({r['canonical_smiles'] for r in rows}) == len(rows)
    generator = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048, includeChirality=True)
    fps = [generator.GetFingerprint(r['mol']) for r in rows]
    metric_rows, predictions, assignments, fitted, compositions = [], [], [], [], []
    for method in ['random', 'scaffold']:
        representative_seeds = {}
        for seed in SEEDS:
            train, test = split_indices(rows, method, seed)
            train_ids = {rows[i]['canonical_smiles'] for i in train}
            test_ids = {rows[i]['canonical_smiles'] for i in test}
            assert not train_ids & test_ids, 'identity leakage'
            representative = representative_seeds.setdefault(frozenset(test_ids), seed)
            n_acyclic = sum(rows[i]['scaffold'] == '__ACYCLIC__' for i in test)
            compositions.append({'split': method, 'seed': seed, 'n_test': len(test),
                                 'n_cyclic': len(test) - n_acyclic, 'n_acyclic': n_acyclic,
                                 'representative_seed': representative})
            train_cores = {rows[i]['scaffold'] for i in train}
            test_cores = {rows[i]['scaffold'] for i in test}
            overlap = len(train_cores & test_cores)
            if method == 'scaffold':
                assert overlap == 0, 'scaffold leakage'
            for subset, indices in [('train', train), ('test', test)]:
                assignments.extend({'split': method, 'seed': seed, 'id': rows[i]['id'],
                                    'subset': subset, 'scaffold': rows[i]['scaffold']} for i in indices)
            # Stable sorting of equal similarities now uses canonical SMILES
            # order, independent of the permutation returned by the split.
            neighbor_train = np.array(sorted(train, key=lambda i: rows[i]['canonical_smiles']))
            train_fps = [fps[j] for j in neighbor_train]
            sims = np.array([DataStructs.BulkTanimotoSimilarity(fps[i], train_fps) for i in test])
            assert sims.min() >= 0 and sims.max() <= 1
            nearest = sims.max(axis=1)
            knn_order = np.argsort(-sims, axis=1, kind='stable')[:, :5]
            knn_pred = y[neighbor_train][knn_order].mean(axis=1)
            ridge_pred, params = ridge_fit_predict(x[train], y[train], x[test])
            fitted.append({'split': method, 'seed': seed, 'train_ids': [rows[i]['id'] for i in train], **params})
            model_predictions = {'training_mean': np.full(len(test), y[train].mean()),
                                 'descriptors_ridge': ridge_pred, 'morgan_5nn': knn_pred}
            for model, pred in model_predictions.items():
                mae, rmse = metrics(y[test], pred)
                metric_rows.append({'split': method, 'seed': seed, 'model': model,
                                    'n_train': len(train), 'n_test': len(test), 'MAE_logS': mae,
                                    'RMSE_logS': rmse, 'scaffold_overlap_groups': overlap,
                                    'identity_overlap': 0, 'mean_nearest_train_tanimoto': float(nearest.mean())})
                for k, index in enumerate(test):
                    predictions.append({'split': method, 'seed': seed, 'model': model, 'id': rows[index]['id'],
                                        'name': rows[index]['name'], 'canonical_smiles': rows[index]['canonical_smiles'],
                                        'measured_logS': y[index], 'predicted_logS': float(pred[k]),
                                        'absolute_error': float(abs(pred[k] - y[index])),
                                        'nearest_train_tanimoto': float(nearest[k]), 'scaffold': rows[index]['scaffold'],
                                        'n_heavy_atoms': rows[index]['n_heavy_atoms'], 'formal_charge': rows[index]['formal_charge']})
    summary = []
    for method in ['random', 'scaffold']:
        representatives = {c['representative_seed'] for c in compositions if c['split'] == method}
        for model in MODELS:
            group = [m for m in metric_rows if m['split'] == method and m['model'] == model
                     and m['seed'] in representatives]
            summary.append({'split': method, 'model': model,
                            'n_seeds': len(SEEDS), 'n_distinct_splits': len(group),
                            'MAE_mean': float(np.mean([m['MAE_logS'] for m in group])),
                            'MAE_sd': float(np.std([m['MAE_logS'] for m in group], ddof=1)) if len(group) > 1 else None,
                            'RMSE_mean': float(np.mean([m['RMSE_logS'] for m in group])),
                            'RMSE_sd': float(np.std([m['RMSE_logS'] for m in group], ddof=1)) if len(group) > 1 else None})
    failures = []
    for method in ['random', 'scaffold']:
        for model in ['descriptors_ridge', 'morgan_5nn']:
            group = [p for p in predictions if p['split'] == method and p['model'] == model and p['seed'] == 42]
            failures.extend(sorted(group, key=lambda p: p['absolute_error'], reverse=True)[:10])
    write_csv(out / 'metrics.csv', metric_rows)
    write_csv(out / 'summary.csv', summary)
    write_csv(out / 'predictions.csv', predictions)
    write_csv(out / 'split_assignments.csv', assignments)
    write_csv(out / 'split_composition.csv', compositions)
    write_csv(out / 'failure_samples.csv', failures)
    strata = []
    for method in ['random', 'scaffold']:
        for seed in SEEDS:
            for model in MODELS:
                group = [p for p in predictions if p['split'] == method and p['seed'] == seed and p['model'] == model]
                definitions = [('nearest_T_le_0.4', lambda p: p['nearest_train_tanimoto'] <= LOW_SIMILARITY_MAX),
                               ('nearest_T_gt_0.4', lambda p: p['nearest_train_tanimoto'] > LOW_SIMILARITY_MAX),
                               ('heavy_atoms_le_15', lambda p: p['n_heavy_atoms'] <= 15),
                               ('heavy_atoms_gt_15', lambda p: p['n_heavy_atoms'] > 15),
                               ('formal_charge_zero', lambda p: p['formal_charge'] == 0),
                               ('formal_charge_nonzero', lambda p: p['formal_charge'] != 0)]
                for name, predicate in definitions:
                    subset = [p for p in group if predicate(p)]
                    if subset:
                        mae, rmse = metrics(np.array([p['measured_logS'] for p in subset]),
                                            np.array([p['predicted_logS'] for p in subset]))
                        strata.append({'split': method, 'seed': seed, 'model': model, 'stratum': name,
                                       'n': len(subset), 'MAE_logS': mae, 'RMSE_logS': rmse})
    write_csv(out / 'stratified_metrics.csv', strata)
    (out / 'ridge_parameters.json').write_text(json.dumps(fitted, indent=2), encoding='utf-8')
    manifest = {'run_utc': datetime.now(timezone.utc).isoformat(), 'source_url': SOURCE,
                'source_git_blob_sha': SOURCE_BLOB,
                'sha256': hashlib.sha256(args.data.read_bytes()).hexdigest(),
                'python_version': platform.python_version(), 'rdkit_version': rdBase.rdkitVersion,
                'numpy_version': np.__version__, 'raw_rows': len(raw), 'kept_rows': len(rows),
                'duplicates_removed': len(duplicates), 'rejected_rows': len(rejected),
                'target': TARGET, 'target_unit': 'log10(mol/L)', 'features': FEATURES,
                'ignored_columns': [k for k in raw[0] if k not in ['Compound ID', 'smiles', TARGET]],
                'parameters': {'ridge_alpha': 1.0, 'knn_k': 5, 'radius': 2, 'fpSize': 2048,
                               'knn_tie_break': 'canonical_isomeric_smiles_ascending',
                               'includeChirality': True, 'seeds': SEEDS, 'nominal_train_fraction': .8,
                               'summary_weighting': 'one row per distinct test ID set within each split method',
                               'descriptive_strata': {'nearest_T': LOW_SIMILARITY_MAX, 'low_T_inclusive': True,
                                                      'heavy_atoms': 15, 'formal_charge': 0}},
                'checks': 'identity disjoint; scaffold disjoint for grouped split; finite values; training-only scaling: passed',
                'limitations': ['Educational benchmark, not a state-of-the-art comparison.',
                                'No hyperparameter tuning. Fixed settings may favor one baseline.',
                                'Methods differ as well as representations; no causal attribution to representation alone.',
                                'No temperature/pH/crystal metadata in this processed table.',
                                'Acyclic compounds are held as one group; scaffold proportions can differ from 80/20.',
                                'Distinct partitions can differ in test composition. Their SD is descriptive, not prediction uncertainty.',
                                'Duplicates keep first; inconsistent labels are audited, not assumed equivalent.']}
    (out / 'run_manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    (out / 'summary.json').write_text(json.dumps({'manifest': manifest, 'metrics': metric_rows, 'summary': summary,
                                               'split_composition': compositions,
                                               'failures': failures}, ensure_ascii=False, indent=2), encoding='utf-8')
    make_plots(out, predictions)
    print(json.dumps({'raw': len(raw), 'kept': len(rows), 'duplicates': len(duplicates), 'summary': summary,
                      'checks': manifest['checks']}, indent=2))


def make_plots(out, predictions):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.family': 'Times New Roman', 'font.size': 9, 'svg.fonttype': 'none',
                         'svg.hashsalt': 'ch06-esol'})
    fig, axes = plt.subplots(3, 2, figsize=(10, 10), sharex=True, sharey=True)
    for row, model in enumerate(MODELS):
        for col, method in enumerate(['random', 'scaffold']):
            data = [p for p in predictions if p['seed'] == 42 and p['split'] == method and p['model'] == model]
            ax = axes[row, col]
            points = ax.scatter([p['measured_logS'] for p in data], [p['predicted_logS'] for p in data],
                                c=[p['nearest_train_tanimoto'] for p in data], cmap='viridis', vmin=0, vmax=1,
                                s=12, alpha=.8, rasterized=False)
            ax.plot([-12, 3], [-12, 3], '--', color='#b47752', lw=1)
            ax.set(xlim=(-12, 3), ylim=(-12, 3), title=f'{method} / {model} / seed 42',
                   xlabel='Measured log10 S (mol/L)', ylabel='Predicted log10 S (mol/L)')
            ax.grid(alpha=.15)
    fig.suptitle('ESOL: fixed baselines, identity-deduplicated data; no test-set tuning', y=.96)
    fig.subplots_adjust(hspace=.35, wspace=.28, right=.82, top=.92)
    colorbar_axis = fig.add_axes([.90, .25, .018, .50])
    fig.colorbar(points, cax=colorbar_axis, label='Nearest training Tanimoto')
    svg = StringIO()
    fig.savefig(svg, format='svg', bbox_inches='tight', metadata={'Date': None})
    svg_text = '\n'.join(line.rstrip() for line in svg.getvalue().splitlines()) + '\n'
    (out / 'prediction_diagnostics.svg').write_text(svg_text, encoding='utf-8', newline='\n')
    fig.savefig(out / 'prediction_diagnostics.png', dpi=150, bbox_inches='tight')
    plt.close(fig)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, default=Path(__file__).resolve().parents[2] / 'data/ch06/delaney-processed.csv')
    parser.add_argument('--output', type=Path, default=Path('results/esol'))
    run(parser.parse_args())
