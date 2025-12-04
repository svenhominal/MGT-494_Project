"""
Translation of `analysis_markups.do` to Python.

Computes markup-related statistics from the passthrough results and writes
LaTeX tables matching the original Stata outputs.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd

from utils import DATA_DIR, TABLE_DIR, ensure_output_dirs, fmt, load_stata, write_text


np.random.seed(42)


RENAMES = {
    f"v{i}": name
    for i, name in enumerate(
        [
            "year",
            "month",
            "day",
            "hour",
            "price0",
            "price1",
            "price2",
            "pricea0",
            "pricea1",
            "pricea2",
            "demand0",
            "demand1",
            "demand2",
            "eratem",
            "slope1_0",
            "slope1_1",
            "slope1_2",
            "qfirm1_0",
            "qfirm1_1",
            "qfirm1_2",
            "slope2_0",
            "slope2_1",
            "slope2_2",
            "qfirm2_0",
            "qfirm2_1",
            "qfirm2_2",
            "slope3_0",
            "slope3_1",
            "slope3_2",
            "qfirm3_0",
            "qfirm3_1",
            "qfirm3_2",
            "slope4_0",
            "slope4_1",
            "slope4_2",
            "qfirm4_0",
            "qfirm4_1",
            "qfirm4_2",
        ],
        start=1,
    )
}


def _rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Rename v1, v2... columns if needed."""
    if set(df.columns).issuperset(set(RENAMES.keys())):
        return df.rename(columns=RENAMES)
    return df


def _compute_logs(df: pd.DataFrame) -> None:
    """Compute log prices for scenarios 0-2."""
    for s in range(3):
        df[f"lprice{s}"] = np.log(df[f"price{s}"])


def _compute_elasticities(df: pd.DataFrame) -> None:
    """Construct elasticities, markups, and related logs."""
    for f in range(1, 5):
        for s in range(3):
            price = df[f"price{s}"]
            slope = df[f"slope{f}_{s}"]
            qfirm = df[f"qfirm{f}_{s}"]
            df[f"elas{f}_{s}"] = slope * price / qfirm
            df[f"lelas{f}_{s}"] = np.log(df[f"elas{f}_{s}"])
            df[f"markup{f}_{s}"] = qfirm / slope
            df[f"lmarkup{f}_{s}"] = np.log(df[f"markup{f}_{s}"])
            df[f"lslope{f}_{s}"] = np.log(1 / slope)
            df[f"lqfirm{f}_{s}"] = np.log(qfirm)


def _compute_changes(df: pd.DataFrame) -> None:
    """Compute percent changes used in the summary tables."""
    for f in range(1, 5):
        df[f"superelas{f}"] = ((df[f"elas{f}_1"] - df[f"elas{f}_0"]) / df[f"elas{f}_0"]) / (
            (df["price1"] - df["price0"]) / df["price0"]
        )
        df[f"superelas_fix{f}"] = ((df[f"elas{f}_2"] - df[f"elas{f}_0"]) / df[f"elas{f}_0"]) / (
            (df["price2"] - df["price0"]) / df["price0"]
        )
        df[f"chqfirm{f}"] = ((df[f"qfirm{f}_1"] - df[f"qfirm{f}_0"]) / df[f"qfirm{f}_0"]) * 100
        df[f"chslope{f}"] = ((df[f"slope{f}_1"] - df[f"slope{f}_0"]) / df[f"slope{f}_0"]) * 100
        df[f"chmarkup{f}"] = ((df[f"markup{f}_1"] - df[f"markup{f}_0"]) / df[f"markup{f}_0"]) * 100
        df[f"deltaqfirm{f}"] = df[f"qfirm{f}_1"] - df[f"qfirm{f}_0"]
        df[f"deltaslope{f}"] = df[f"slope{f}_1"] - df[f"slope{f}_0"]
        df[f"deltamarkup{f}"] = df[f"markup{f}_1"] - df[f"markup{f}_0"]
    df["chdemand"] = ((df["demand1"] - df["demand0"]) / df["demand0"]) * 100


def _merge_eprice(df: pd.DataFrame) -> pd.DataFrame:
    """Attach emissions price data."""
    eua = load_stata("data_eua_prices.dta")[["year", "month", "day", "eprice"]]
    merged = df.merge(eua, on=["year", "month", "day"], how="left")
    merged.loc[merged["year"] == 2004, "eprice"] = 0
    merged["leprice"] = np.log(merged["eprice"].fillna(0) + 1)
    return merged


def _elas_table(df: pd.DataFrame) -> str:
    """Create LaTeX table for elasticity summary statistics."""
    lines: List[str] = [
        "\\begin{table}",
        "\\centering",
        "\\caption{Elaticity Summary Statistics} \\label{tab:elas}",
        "\\begin{tabular*}{.9\\textwidth}{@{\\extracolsep{\\fill}} l c c c c c}",
        "\\hline\\hline ",
        "& \\textbf{Obs}  & \\textbf{Mean}  & \\textbf{SD}  & \\textbf{Min}  & \\textbf{Max} \\\\",
        "\\cline{2-6} \\\\[-\\sep]",
    ]
    for f in range(1, 5):
        series = df[f"elas{f}_0"].dropna()
        lower = np.nanpercentile(series, 1)
        upper = np.nanpercentile(series, 99)
        trimmed = series[(series > lower) & (series < upper)]
        lines.append(
            f"Firm {f} $(\\eta_{f})$  & {int(trimmed.count()):6d} & {trimmed.mean():4.1f} & "
            f"{trimmed.std():4.1f} & {trimmed.min():4.1f} & {trimmed.max():4.1f} \\\\[\\sep]"
        )
    lines += [
        "\\hline\\hline \\vspace{-18pt}",
        "\\end{tabular*}",
        "\\begin{minipage}[c]{.9\\textwidth}",
        "{\\footnotesize \\vspace{6pt}",
        "\\noindent",
        "Notes: Sample from January 2004 to February 2006, includes all thermal units in the Spanish electricity market. ",
        "Slope of residual demand estimated using a Gaussian Kernel with bandwidth set to 3\\euro.}",
        "\\end{minipage}",
        "\\end{table}",
    ]
    return "\n".join(lines)


def _summary_stats(series: pd.Series) -> Dict[str, float]:
    """Return mean, sd, p25, p50, p75."""
    return {
        "mean": series.mean(),
        "sd": series.std(),
        "p25": series.quantile(0.25),
        "p50": series.quantile(0.5),
        "p75": series.quantile(0.75),
    }


def _qfirm_table(df: pd.DataFrame) -> str:
    """Create LaTeX table for percent changes in quantities, markups, and slopes."""
    lines: List[str] = [
        "\\begin{table}",
        "\\centering",
        "\\caption{Percent Changes in Quantities, Markups and Slopes} \\label{tab:qfirm}",
        "\\begin{tabular*}{.9\\textwidth}{@{\\extracolsep{\\fill}} l c c c c c}",
        "\\hline\\hline ",
        "& \\textbf{Mean}  & \\textbf{SD}  & \\textbf{P25}  & \\textbf{P50} & \\textbf{P75}  \\\\",
        "\\cline{2-6} \\\\[-\\sep]",
        "\\textbf{Changes in Quantity }  \\\\[\\sep]",
    ]
    stats = _summary_stats(df["chdemand"].dropna())
    lines.append(
        f"\\quad Aggregate Demand  & {stats['mean']:4.1f}\\% & {stats['sd']:4.1f}\\% & "
        f"{stats['p25']:4.1f}\\% & {stats['p50']:4.1f}\\% & {stats['p75']:4.1f}\\% \\\\[\\sep]"
    )
    for f in range(1, 5):
        stats = _summary_stats(df[f"chqfirm{f}"].dropna())
        lines.append(
            f"\\quad Firm {f}  & {stats['mean']:4.1f}\\% & {stats['sd']:4.1f}\\% & "
            f"{stats['p25']:4.1f}\\% & {stats['p50']:4.1f}\\% & {stats['p75']:4.1f}\\% \\\\[\\sep]"
        )
    lines.append("\\hline \\\\[-\\sep]")
    lines.append("\\textbf{Changes in Slope} \\\\ \\textbf{of Inverse Residual Demand} \\\\[\\sep]")
    for f in range(1, 5):
        stats = _summary_stats(df[f"chslope{f}"].dropna())
        lines.append(
            f"\\quad Firm {f}  & {stats['mean']:4.1f}\\% & {stats['sd']:4.1f}\\% & "
            f"{stats['p25']:4.1f}\\% & {stats['p50']:4.1f}\\% & {stats['p75']:4.1f}\\% \\\\[\\sep]"
        )
    lines.append("\\hline \\\\[-\\sep]")
    lines.append("\\textbf{Changes in Markup}  \\\\[\\sep]")
    for f in range(1, 5):
        stats = _summary_stats(df[f"chmarkup{f}"].dropna())
        lines.append(
            f"\\quad Firm {f}  & {stats['mean']:4.1f}\\% & {stats['sd']:4.1f}\\% & "
            f"{stats['p25']:4.1f}\\% & {stats['p50']:4.1f}\\% & {stats['p75']:4.1f}\\% \\\\[\\sep]"
        )
    lines += [
        "\\hline\\hline \\vspace{-18pt}",
        "\\end{tabular*}",
        "\\begin{minipage}[c]{.9\\textwidth}",
        "{\\footnotesize \\vspace{6pt}",
        "\\noindent",
        "Notes: Sample from January 2004 to February 2006, includes all thermal units in the Spanish electricity market. ",
        "Table expresses percent changes in quantities, markups and the slope of the inverse residual demand for a one euro ",
        "increase in carbon prices. Number of observations: 18,960. } \\end{minipage}",
        "\\end{table}",
    ]
    return "\n".join(lines)


def main() -> None:
    """
    Compute markup statistics and export LaTeX tables.
    """
    ensure_output_dirs()
    # Prefer the already-created Stata dataset; fallback to CSV if needed.
    data_path = DATA_DIR / "passthrough_results.dta"
    if data_path.exists():
        df = pd.read_stata(data_path)
    else:
        df = pd.read_csv(DATA_DIR.parent / "matlab_data" / "passthrough_results.csv", header=None)
    df = _rename_columns(df)
    _compute_logs(df)
    _compute_elasticities(df)
    _compute_changes(df)
    df = _merge_eprice(df)

    elas_table = _elas_table(df)
    qfirm_table = _qfirm_table(df)
    write_text(TABLE_DIR / "table_elas.tex", elas_table)
    write_text(TABLE_DIR / "table_qfirm.tex", qfirm_table)


if __name__ == "__main__":
    main()
