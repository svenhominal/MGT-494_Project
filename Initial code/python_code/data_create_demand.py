from __future__ import annotations

"""
Translation of `stata_code/data_create_demand.do`.

Purpose: Build aggregate market outcomes (hourly demand and market price) by parsing
daily ENE files, adjusting for bilateral contracts, and saving to `stata_data/data_market.dta`.

This script depends on raw ENE/PDBF files under config.DATAPATH and is provided as a
scaffold pending access to those files.
"""

from utils import setup


def main():
    setup()
    raise NotImplementedError(
        "data_create_demand: requires raw ENE and PDBF files under config.DATAPATH."
    )


if __name__ == "__main__":
    main()

