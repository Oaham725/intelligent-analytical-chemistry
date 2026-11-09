#!/usr/bin/env python3
"""第六章异构体表示实验：真实 RDKit 计算，不训练性质预测模型。

运行：python -m pip install rdkit
     python case_study.py --output results
依赖：Python 3.10+、RDKit。输出描述符、手性/非手性指纹相似度及结构图。
"""
import argparse
import csv
import json
from pathlib import Path

from rdkit import Chem, DataStructs, rdBase
from rdkit.Chem import Descriptors, Draw, rdFingerprintGenerator

MOLECULES = [
    ("ethanol", "CCO", "connectivity"),
    ("dimethyl_ether", "COC", "connectivity"),
    ("E_2_butene", "C/C=C/C", "double_bond_stereo"),
    ("Z_2_butene", "C/C=C\\C", "double_bond_stereo"),
    ("lactic_A", "C[C@H](O)C(=O)O", "enantiomer"),
    ("lactic_B", "C[C@@H](O)C(=O)O", "enantiomer"),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("results"))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    mols = [Chem.MolFromSmiles(smi) for _, smi, _ in MOLECULES]
    if any(mol is None for mol in mols):
        raise ValueError("Invalid input SMILES")
    rows = []
    for (name, smiles, pair), mol in zip(MOLECULES, mols):
        rows.append({"name": name, "input_SMILES": smiles, "pair_type": pair,
                     "canonical_isomeric_SMILES": Chem.MolToSmiles(mol, isomericSmiles=True),
                     "canonical_no_stereo": Chem.MolToSmiles(mol, isomericSmiles=False),
                     "MW_g_mol": round(Descriptors.MolWt(mol), 4),
                     "HBD": Descriptors.NumHDonors(mol),
                     "HBA": Descriptors.NumHAcceptors(mol),
                     "TPSA_A2": round(Descriptors.TPSA(mol), 4)})
    with (args.output / "descriptors.csv").open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    # 固定参数；isomeric SMILES中指定的双键/原子立体信息由RDKit处理。
    comparisons = []
    all_fps = {}
    for chirality in (False, True):
        generator = rdFingerprintGenerator.GetMorganGenerator(
            radius=2, fpSize=2048, includeChirality=chirality)
        fps = [generator.GetFingerprint(mol) for mol in mols]
        all_fps[chirality] = fps
        for a, b in ((0, 1), (2, 3), (4, 5)):
            comparisons.append({"molecule_A": MOLECULES[a][0], "molecule_B": MOLECULES[b][0],
                                "includeChirality": chirality,
                                "Tanimoto_binary": DataStructs.TanimotoSimilarity(fps[a], fps[b])})
    with (args.output / "fingerprint_comparisons.csv").open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(comparisons[0]))
        writer.writeheader()
        writer.writerows(comparisons)

    # 有化学意义的检查：组成相同并不意味着官能团相同；镜像信息需显式保留。
    assert abs(rows[0]["MW_g_mol"] - rows[1]["MW_g_mol"]) < 1e-8
    assert (rows[0]["HBD"], rows[1]["HBD"]) == (1, 0)
    assert abs(rows[0]["TPSA_A2"] - 20.23) < 0.01
    assert abs(rows[1]["TPSA_A2"] - 9.23) < 0.01
    assert rows[4]["canonical_no_stereo"] == rows[5]["canonical_no_stereo"]
    assert rows[4]["canonical_isomeric_SMILES"] != rows[5]["canonical_isomeric_SMILES"]
    assert DataStructs.TanimotoSimilarity(all_fps[False][4], all_fps[False][5]) == 1.0
    assert DataStructs.TanimotoSimilarity(all_fps[True][4], all_fps[True][5]) < 1.0
    assert DataStructs.TanimotoSimilarity(all_fps[True][0], all_fps[True][1]) < 1.0
    assert DataStructs.TanimotoSimilarity(all_fps[False][2], all_fps[False][3]) == 1.0
    assert DataStructs.TanimotoSimilarity(all_fps[True][2], all_fps[True][3]) < 1.0
    image = Draw.MolsToGridImage(mols, molsPerRow=2, subImgSize=(380, 250),
                                legends=[row[0] for row in MOLECULES], useSVG=True)
    (args.output / "molecule_pairs.svg").write_text(image, encoding="utf-8")
    manifest = {"rdkit_version": rdBase.rdkitVersion, "radius": 2, "fpSize": 2048,
                "includeChirality": [False, True], "fingerprint_type": "binary Morgan",
                "structure_policy": "As provided; neutral examples; stereo retained; no salt stripping",
                "molecules": len(mols), "assertions": "passed",
                "limitations": ["Not a predictive model or benchmark.",
                                "Six selected molecules do not define a meaningful scaffold split.",
                                "Browser demo uses a separate toy WL/FNV algorithm."]}
    (args.output / "run_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(manifest, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
