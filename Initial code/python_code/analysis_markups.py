from __future__ import annotations

import numpy as np
import pandas as pd

from config import MATLAB_DATA_DIR
from utils import latex_table, load_stata, setup, write_text


def load_passthrough_results() -> pd.DataFrame:
    """
    Load from Matlab CSV if present; otherwise fall back to Stata
    `stata_data/passthrough_results.dta` which contains the same columns.
    """
    p = MATLAB_DATA_DIR / "passthrough_results.csv"
    if p.exists():
        df = pd.read_csv(p, header=None)
        cols = [
            "year", "month", "day", "hour",
            "price0", "price1", "price2",
            "pricea0", "pricea1", "pricea2",
            "demand0", "demand1", "demand2",
            "eratem",
        ]
        for f in range(1, 5):
            for s in range(0, 3):
                cols.append(f"slope{f}_{s}")
        for f in range(1, 5):
            for s in range(0, 3):
                cols.append(f"qfirm{f}_{s}")
        df.columns = cols
        return df
    # Fallback to .dta produced by Stata analysis_markups.do
    return load_stata("passthrough_results.dta")


def compute_derived(df: pd.DataFrame) -> pd.DataFrame:
    for s in (0, 1, 2):
        df[f"lprice{s}"] = np.log(df[f"price{s}"])  # noqa: F841
    for f in (1, 2, 3, 4):
        for s in (0, 1, 2):
            # Elasticity eta = slope * price / q
            df[f"elas{f}_{s}"] = df[f"slope{f}_{s}"] * df[f"price{s}"] / df[f"qfirm{f}_{s}"]
            df[f"lelas{f}_{s}"] = np.log(df[f"elas{f}_{s}"])
            df[f"markup{f}_{s}"] = df[f"qfirm{f}_{s}"] / df[f"slope{f}_{s}"]
            df[f"lmarkup{f}_{s}"] = np.log(df[f"markup{f}_{s}"])
            df[f"lslope{f}_{s}"] = np.log(1.0 / df[f"slope{f}_{s}"])
            df[f"lqfirm{f}_{s}"] = np.log(df[f"qfirm{f}_{s}"])

        # Changes from 0 -> 1, and fixed-2 vs 0
        df[f"superelas{f}"] = ((df[f"elas{f}_1"] - df[f"elas{f}_0"]) / df[f"elas{f}_0"]) / (
            (df["price1"] - df["price0"]) / df["price0"]
        )
        df[f"superelas_fix{f}"] = ((df[f"elas{f}_2"] - df[f"elas{f}_0"]) / df[f"elas{f}_0"]) / (
            (df["price2"] - df["price0"]) / df["price0"]
        )
        df[f"chqfirm{f}"] = ((df[f"qfirm{f}_1"] - df[f"qfirm{f}_0"]) / df[f"qfirm{f}_0"]) * 100
        df[f"chslope{f}"] = ((df[f"slope{f}_1"] - df[f"slope{f}_0"]) / df[f"slope{f}_0"]) * 100
        df[f"chmarkup{f}"] = ((df[f"markup{f}_1"] - df[f"markup{f}_0"]) / df[f"markup{f}_0"]) * 100
        df[f"deltaqfirm{f}"] = (df[f"qfirm{f}_1"] - df[f"qfirm{f}_0"])  # noqa: F841
        df[f"deltaslope{f}"] = (df[f"slope{f}_1"] - df[f"slope{f}_0"])  # noqa: F841
        df[f"deltamarkup{f}"] = (df[f"markup{f}_1"] - df[f"markup{f}_0"])  # noqa: F841

    df["chdemand"] = ((df["demand1"] - df["demand0"]) / df["demand0"]) * 100
    return df


def merge_eu_ets_prices(df: pd.DataFrame) -> pd.DataFrame:
    p = load_stata("data_eua_prices.dta")[ ["year", "month", "day", "eprice"] ]
    out = df.merge(p, on=["year", "month", "day"], how="left")
    out.loc[out["year"] == 2004, "eprice"] = 0
    out["leprice"] = np.log(out["eprice"] + 1)
    return out


def table_elasticities(df: pd.DataFrame):
    header = " & \\textbf{Obs} & \\textbf{Mean} & \\textbf{SD} & \\textbf{Min} & \\textbf{Max}"
    rows = []
    for f in (1, 2, 3, 4):
        x = df[f"elas{f}_0"].copy()
        lower, upper = np.nanpercentile(x, [1, 99])
        x = x[(x > lower) & (x < upper)]
        cells = [f"Firm {f} $(\\eta_{f})$"]
        cells += [f" {len(x):,.0f}", f" {np.nanmean(x):0.1f}", f" {np.nanstd(x):0.1f}",
                  f" {np.nanmin(x):0.1f}", f" {np.nanmax(x):0.1f}"]
        rows.append(cells)
    tex = latex_table(header, rows, caption="Elasticity Summary Statistics", label="tab:elas")
    write_text("table_elas.tex", tex)


def table_qfirm(df: pd.DataFrame):
    header = " & \\textbf{Mean} & \\textbf{SD} & \\textbf{P25} & \\textbf{P50} & \\textbf{P75}"
    rows = []

    def fmt_stats(title: str, x: pd.Series):
        cells = [title]
        cells += [
            f" {np.nanmean(x):0.1f}\\%",
            f" {np.nanstd(x):0.1f}\\%",
            f" {np.nanpercentile(x, 25):0.1f}\\%",
            f" {np.nanpercentile(x, 50):0.1f}\\%",
            f" {np.nanpercentile(x, 75):0.1f}\\%",
        ]
        rows.append(cells)

    fmt_stats("\\textbf{Changes in Quantity} \\ \quad Aggregate Demand", df["chdemand"])
    for f in (1, 2, 3, 4):
        fmt_stats(f"\\quad Firm {f}", df[f"chqfirm{f}"])
    rows.append(["\\hline"])  # separator
    rows.append(["\\textbf{Changes in Slope of Inverse Residual Demand}"])
    for f in (1, 2, 3, 4):
        fmt_stats(f"\\quad Firm {f}", df[f"chslope{f}"])
    rows.append(["\\hline"])  # separator
    rows.append(["\\textbf{Changes in Markup}"])
    for f in (1, 2, 3, 4):
        fmt_stats(f"\\quad Firm {f}", df[f"chmarkup{f}"])

    tex = latex_table(header, rows, caption="Percent Changes in Quantities, Markups and Slopes",
                      label="tab:qfirm")
    write_text("table_qfirm.tex", tex)


def main():
    setup()
    df = load_passthrough_results()
    df = compute_derived(df)
    df = merge_eu_ets_prices(df)
    table_elasticities(df)
    table_qfirm(df)


if __name__ == "__main__":
    main()
