from __future__ import annotations

"""
Translation of `stata_code/data_create.do` to Python.

Note: This script depends on raw bidding and bilateral contract files located under the
original Stata `$datapath` (e.g., .../data_sem/curva_pbc_uof, .../data_sem/pdbf, ...).
These raw files are not typically included in this repository. The code below outlines
the pipeline and provides function scaffolding to implement the same logic when raw
data is available locally.

Steps (summary):
- Iterate dates 2004–2007 (Jan–Jun 2007), load offer curve files (`curva_pbc_uof_YYYYMMDD.1`).
- Parse columns: hour, date, UP id, type (S/D), quantity (MWh), price (€/MWh×10), accepted flag.
- Handle missing hours (add hour 24 if needed).
- Merge bilateral contract quantities per (up, hour) from PDBF files, apply regulatory filters.
- Merge firm info per UP and month (ownership shares, firm codes), expand to multiple owners.
- Compute market-clearing price per hour and flags for rejected bids.
- Compute cumulative MWh across price steps per unit and direction; add bilateral to cumulated quantities.
- Convert MWh by ownership shares; compute firm net quantities and aggregate demand/supply.
- Smooth demand and supply via piecewise-linear fits over price bins; compute residual demand slope.
- Merge thermal plant characteristics and filter to active thermal plants.
- Append to monthly auxiliary datasets and persist in `stata_data/auxiliary`.

Implementations of loaders for the proprietary `.1` files and detailed filters are omitted here.
"""

from pathlib import Path

import pandas as pd

from config import DATAPATH, DIRPATH, STATA_DATA_DIR
from utils import setup


def main():
    setup()
    raise NotImplementedError(
        "data_create: raw market files are required (curva_pbc_uof, pdbf, firm lists). "
        "Set config.DATAPATH to your local raw data folder and implement the loaders."
    )


if __name__ == "__main__":
    main()

