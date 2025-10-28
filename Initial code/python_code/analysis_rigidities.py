from __future__ import annotations

import pandas as pd
import numpy as np

from utils import load_stata, write_text, latex_table, setup


def compute_adjustments(df: pd.DataFrame) -> pd.DataFrame:
    # Median price per unit-day-hour as proxy for 'medprice'
    grp_keys = ["up", "year", "month", "day", "hour"]
    med = df.groupby(grp_keys)["price"].median().rename("medprice").reset_index()
    df = df.merge(med, on=grp_keys, how="left")

    # Collapse to unit-hour-day level means (as in Stata collapse)
    keep_cols = [
        "price", "medprice", "accepted", "rejected", "bilateral", "erate", "cost_CO2", "eprice", "weekd", "firm", "firm_code", "fuel"
    ]
    agg = df.groupby(["year", "month", "day", "hour", "up", "weekd", "firm", "firm_code", "fuel"], as_index=False)[keep_cols].mean()

    agg["price"] = agg["price"].round(2)
    agg["medprice"] = agg["medprice"].round(2)

    # Build time index
    agg["time"] = pd.to_datetime(dict(year=agg.year, month=agg.month, day=agg.day))
    # id = group(up hour firm)
    agg["id"] = agg.groupby(["up", "hour", "firm"]).ngroup() + 1

    # Previous day same hour comparison
    agg = agg.sort_values(["id", "time"])  # ts order
    agg["price_lag"] = agg.groupby("id")["price"].shift(1)
    agg["medprice_lag"] = agg.groupby("id")["medprice"].shift(1)

    agg["adj1"] = np.where(~agg["price_lag"].isna(), (agg["price"] != agg["price_lag"]).astype(int), np.nan)
    agg["adj2"] = np.where(~agg["medprice_lag"].isna(), (agg["medprice"] != agg["medprice_lag"]).astype(int), np.nan)

    # Previous week same weekday, same hour, same unit at firm-level grouping
    agg = agg.sort_values(["id", "weekd", "year", "month", "day"])  # for week indexing
    agg["weekid"] = agg.groupby(["id", "weekd"]).cumcount() + 1

    # id2 = group(up hour firm weekd)
    agg["id2"] = agg.groupby(["up", "hour", "firm", "weekd"]).ngroup() + 1
    agg = agg.sort_values(["id2", "weekid"])  # ts order for weekly
    agg["price_lag_w"] = agg.groupby("id2")["price"].shift(1)
    agg["medprice_lag_w"] = agg.groupby("id2")["medprice"].shift(1)

    agg["adj3"] = np.where(~agg["price_lag_w"].isna(), (agg["price"] != agg["price_lag_w"]).astype(int), np.nan)
    agg["adj4"] = np.where(~agg["medprice_lag_w"].isna(), (agg["medprice"] != agg["medprice_lag_w"]).astype(int), np.nan)

    # Firm-level indicator of any unit price change on a given day/hour/firm (max over units)
    k = agg.groupby(["hour", "year", "month", "day", "firm"]).agg(adj5=("adj1", "max"), adj6=("adj2", "max")).reset_index()

    # Attach firm-level indicators back to unit rows for easy filtering by weekday
    agg = agg.merge(k, on=["hour", "year", "month", "day", "firm"], how="left")
    return agg


def write_frequency_table(agg: pd.DataFrame):
    # Build LaTeX with 3 columns: adj1 (prev day unit), adj3 (prev week unit), adj5 (prev day firm)
    header = " & \\multicolumn{1}{c}{Previous Day} & \\multicolumn{1}{c}{Previous Week} & \\multicolumn{1}{c}{Previous Day}"
    rows = []

    def mean_ignore_nan(x: pd.Series) -> float:
        return float(np.nanmean(x)) if x.size else float("nan")

    # All days
    cells = ["All days",
             f" {mean_ignore_nan(agg['adj1']):0.3f}",
             f" {mean_ignore_nan(agg['adj3']):0.3f}",
             f" {mean_ignore_nan(agg['adj5']):0.3f}"]
    rows.append(cells)

    weeknames = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    for w in range(1, 8):
        d = agg[agg["weekd"] == w]
        cells = [f"{weeknames[w-1]}",
                 f" {mean_ignore_nan(d['adj1']):0.3f}",
                 f" {mean_ignore_nan(d['adj3']):0.3f}",
                 f" {mean_ignore_nan(d['adj5']):0.3f}"]
        rows.append(cells)

    tex = latex_table(header, rows, caption="Frequency of Bid Changes", label="tab:frequency")
    write_text("tab_frequency.tex", tex)


def main():
    setup()
    try:
        df = load_stata("data_regressions_lite.dta")
    except FileNotFoundError:
        # Some repos may not include this lightweight dataset.
        return
    agg = compute_adjustments(df)
    write_frequency_table(agg)


if __name__ == "__main__":
    main()

