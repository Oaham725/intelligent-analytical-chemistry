"""Audit spectrum-title matching in Zenodo record 14651816, without fitting a model."""
import argparse
from collections import Counter
from pathlib import Path

from openpyxl import load_workbook


def spectrum_titles(path):
    workbook = load_workbook(path, read_only=True, data_only=True)
    try:
        sheet = workbook.worksheets[0]
        titles = [
            str(row[0]).strip()
            for row in sheet.iter_rows(min_row=2, max_col=1, values_only=True)
            if row[0] is not None and str(row[0]).strip()
        ]
        return Counter(titles)
    finally:
        workbook.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="extracted Data_set_FTIR_Raman directory")
    args = parser.parse_args()
    for study in ("Classification", "Quantification"):
        ir = spectrum_titles(args.root / "FTIR" / f"FTIR_spectra_{study} Study.xlsx")
        raman = spectrum_titles(args.root / "Raman" / f"Raman_spectra_{study} Study.xlsx")
        shared = ir.keys() & raman.keys()
        print(f"{study}:")
        print(f"  FTIR rows={ir.total()}, distinct titles={len(ir)}")
        print(f"  Raman rows={raman.total()}, distinct titles={len(raman)}")
        print(f"  Exact shared titles={len(shared)}")
        print(f"  Titles occurring exactly once in both={sum(ir[key] == raman[key] == 1 for key in shared)}")
        print(f"  Titles only in FTIR={len(ir.keys() - raman.keys())}, only in Raman={len(raman.keys() - ir.keys())}")


if __name__ == "__main__":
    main()
