from __future__ import annotations

"""
Translation of `stata_code/data_create_matlab.do`.

Purpose: Prepare bidding data CSVs for Matlab slope estimation, including enriched unit-,
firm-, and cost information per bid step. Requires raw market files and auxiliary
Stata-derived datasets (costs, inputs, emissions prices, thermal plant attributes).

Key outputs (mirroring Stata outsheet):
- matlab_data/data_YYYYMMDD.csv (fields: year, month, day, hour, firm_code, id, price, mwh, erate, direction, accepted, rejected, mg_cost)
- matlab_data/data_up_YYYYMMDD.csv (fields: up, id)

This is a scaffold: implement loaders and transformations once raw data is available.
"""

from utils import setup


def main():
    setup()
    raise NotImplementedError(
        "data_create_matlab: requires raw market files and derived cost datasets. "
        "Implement once inputs are available locally."
    )


if __name__ == "__main__":
    main()

