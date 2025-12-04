"""
Translation of `analysis_rigidities.do` to Python.

Analyzes bidding rigidities and reports the frequency of bid changes.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd

from utils import DATA_DIR, TABLE_DIR, ensure_output_dirs, fmt, load_stata, write_text


np.random.seed(42)


def _compute_median_price(group: pd.DataFrame) -> float:
    """
    Compute the median price within a bidding curve as in the Stata code.
    """
    threshold = group["medmwh"].iloc[0]
    crossing = group.loc[group["cummwh"] >= threshold]
    price_val = crossing.iloc[0]["price"] if not crossing.empty else np.nan
    first = group.iloc[0]
    if first["cummwh"] >= threshold and first["step"] == 1 and first["bilateral"] == 0:
        price_val = first["price"]
    return price_val


def prepare_data() -> pd.DataFrame:
    """
    Recreate the collapsed bidding dataset used for rigidity analysis.
    """
    df = load_stata("data_regressions_lite.dta")
    df = df.sort_values(["up", "year", "month", "day", "hour", "price"])
    df["step"] = df.groupby(["up", "year", "month", "day", "hour"]).cumcount() + 1
    df["numstep"] = df.groupby(["up", "year", "month", "day", "hour"])["price"].transform("size")
    df["medmwh"] = (df["mw"] - df["minmw"]) / 2 + df["minmw"]

    df["medprice"] = df.groupby(["up", "year", "month", "day", "hour"]).apply(_compute_median_price).reset_index(
        level=[0, 1, 2, 3, 4], drop=True
    )

    collapsed = (
        df.groupby(["year", "month", "day", "hour", "up", "weekd", "firm", "firm_code", "fuel"], as_index=False)
        .agg(
            {
                "price": "mean",
                "medprice": "mean",
                "accepted": "mean",
                "rejected": "mean",
                "bilateral": "mean",
                "erate": "mean",
                "cost_CO2": "mean",
                "eprice": "mean",
                "numstep": "mean",
            }
        )
        .copy()
    )
    collapsed["price"] = collapsed["price"].round(2)
    collapsed["medprice"] = collapsed["medprice"].round(2)
    collapsed["time"] = pd.to_datetime(dict(year=collapsed.year, month=collapsed.month, day=collapsed.day))
    return collapsed


def _lag_change(series: pd.Series) -> pd.Series:
    """
    Indicator for whether the value changed relative to the previous observation.
    """
    lag = series.shift()
    out = pd.Series(np.nan, index=series.index)
    mask = lag.notna()
    out.loc[mask] = (series.loc[mask] != lag.loc[mask]).astype(int)
    return out


def compute_adjustments(collapsed: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """
    Compute adjustment indicators analogous to adj1-adj6 in Stata.
    """
    data = collapsed.sort_values(["up", "hour", "firm", "time"]).copy()
    data["id"] = pd.factorize(list(zip(data["up"], data["hour"], data["firm"])))[0]
    data["adj1"] = data.groupby("id")["price"].transform(_lag_change)
    data["adj2"] = data.groupby("id")["medprice"].transform(_lag_change)

    data = data.sort_values(["id", "weekd", "time"])
    data["weekid"] = data.groupby(["id", "weekd"]).cumcount() + 1
    data["id2"] = pd.factorize(list(zip(data["up"], data["hour"], data["firm"], data["weekd"])))[0]
    data = data.sort_values(["id2", "weekid"])
    data["adj3"] = data.groupby("id2")["price"].transform(_lag_change)
    data["adj4"] = data.groupby("id2")["medprice"].transform(_lag_change)

    firm_level = (
        data.groupby(["hour", "year", "month", "day", "firm", "weekd"])
        .agg({"adj1": "max", "adj2": "max"})
        .rename(columns={"adj1": "adj5", "adj2": "adj6"})
        .reset_index()
    )
    return {"unit": data, "firm": firm_level}


def build_table(adjs: Dict[str, pd.DataFrame]) -> str:
    """
    Build LaTeX table summarizing the frequency of bid changes.
    """
    weeknames = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    cols = [("adj1", "Previous Day"), ("adj3", "Previous Week"), ("adj5", "Previous Day (Firm)")]

    lines: List[str] = [
        "\\begin{table}",
        "\\centering",
        "\\caption{Frequency of Bid Changes}\\label{tab:frequency}",
        "\\begin{tabular*}{0.8\\textwidth}{@{\\extracolsep{\\fill}} lrrr}",
        " \\hline\\hline \\\\[-\\sep] ",
        " & \\multicolumn{1}{c}{{Previous Day}}  & \\multicolumn{1}{c}{{Previous Week}}  & \\multicolumn{1}{c}{{Previous Day}} \\\\",
        " & \\multicolumn{1}{c}{{Unit-Level}}  & \\multicolumn{1}{c}{{Unit-Level}}  & \\multicolumn{1}{c}{{Firm-Level}} ",
        "\\\\ \\cline{2-2} \\cline{3-3} \\cline{4-4} \\\\[-\\sep] ",
    ]
    # All days
    row_vals = ["All days"]
    unit_df = adjs["unit"]
    firm_df = adjs["firm"]
    for key, _ in cols:
        source = firm_df if key == "adj5" else unit_df
        row_vals.append(f"{source[key].mean(skipna=True):4.3f}")
    lines.append(" ".join(row_vals) + "  \\\\[\\sep] ")

    for idx, wname in enumerate(weeknames, start=1):
        row_vals = [f" {wname}"]
        for key, _ in cols:
            source = firm_df if key == "adj5" else unit_df
            mask = source["weekd"] == idx
            row_vals.append(f"{source.loc[mask, key].mean(skipna=True):4.3f}")
        lines.append(" ".join(row_vals) + " \\\\")

    lines += [
        " \\hline\\hline ",
        "\\end{tabular*}",
        "\\begin{minipage}[c]{0.8\\textwidth}",
        "{\\footnotesize ",
        "\\noindent",
        "Notes: Table reports the average frequency of times in which the average or median price bid of a given ",
        "unit changes. The average bid is defined as the average of prices across the supply function ",
        "of a unit. Columns 1 compares the bids with the same hour of the previous day. ",
        "Columns 2 compares the bids with the same hour and weekday of the previous week. ",
        "Columns 3 reports whether any changes occured at the firm level. ",
        "}",
        "\\end{minipage}",
        "\\end{table}",
    ]
    return "\n".join(lines)


def main() -> None:
    """
    Prepare data and write the rigidity frequency table.
    """
    ensure_output_dirs()
    collapsed = prepare_data()
    adjs = compute_adjustments(collapsed)
    table = build_table(adjs)
    write_text(TABLE_DIR / "tab_frequency.tex", table)


if __name__ == "__main__":
    main()
