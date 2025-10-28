from __future__ import annotations

"""
Translation of `stata_code/data_merge.do`.

Purpose: Merge bidding-derived datasets with thermal plant characteristics, input prices,
emissions prices, weather, and demand controls; construct reduced-form datasets for
pass-through and structural analyses; and save:
- stata_data/data_regressions.dta
- stata_data/data_regressions_daily.dta
- stata_data/data_regressions_passthrough.dta
- stata_data/data_regressions_structural.dta

This script assumes that intermediate `.dta` files created by data_create*.py exist.
It is provided as a scaffold; exact merges depend on those inputs.
"""

from utils import setup


def main():
    setup()
    raise NotImplementedError(
        "data_merge: expects intermediate `.dta` files created from raw data. "
        "Implement once upstream data_create scripts are operational."
    )


if __name__ == "__main__":
    main()

