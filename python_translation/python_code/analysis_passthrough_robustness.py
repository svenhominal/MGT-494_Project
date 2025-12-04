"""
Translation of `analysis_passthrough_robustness.do` to Python.

Generates emissions price diagnostics and runs trend-augmented pass-through
regressions.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from analysis_passthrough_rf import _generic_table, run_trend_block
from utils import FIG_DIR, TABLE_DIR, ensure_output_dirs, fmt, load_stata


np.random.seed(42)


def compute_fits(df: pd.DataFrame) -> pd.DataFrame:
    """
    Approximate Stata's fitted values for emissions prices over time.
    """
    df = df.sort_values(["year", "month", "day"]).copy()
    df["time"] = pd.to_datetime(dict(year=df.year, month=df.month, day=df.day))
    df["lfit1"] = df.groupby(["ym", "day"])["eprice"].transform("mean")
    df["error1"] = df["lfit1"] - df["eprice"]

    df["indyb"] = df.sort_values(["yb", "month", "day"]).groupby("yb").cumcount() + 1
    df["lfit2"] = df.groupby(["yb", "indyb"])["eprice"].transform("mean")

    df["indyq"] = df.sort_values(["yq", "month", "day"]).groupby("yq").cumcount() + 1
    df["lfit3"] = df.groupby(["yq", "indyq"])["eprice"].transform("mean")
    return df


def _plot(df: pd.DataFrame, yfit: str, fname: str, title: str) -> None:
    """
    Scatter actual eprice with fitted line.
    """
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.scatter(df["time"], df["eprice"], s=8, alpha=0.4, label="EUA price")
    ax.plot(df["time"], df[yfit], color="red", label="Fitted")
    ax.set_title(title)
    ax.set_xlabel("")
    ax.set_ylabel("Eur/ton")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIG_DIR / fname)
    plt.close(fig)


def generate_graphs(df: pd.DataFrame) -> None:
    """
    Replicate the emissions price diagnostics.
    """
    _plot(df[df["year"] > 2004], "lfit1", "eprice_lfit1_time_all.pdf", "Emissions price fit by month-day")
    reduced = df[(df["year"] > 2004) & (df["rd"] == 0)]
    _plot(reduced, "lfit1", "eprice_lfit1_time.pdf", "Emissions price fit (rd excluded)")
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.scatter(reduced["time"], reduced["error1"], s=8, alpha=0.4)
    ax.set_title("Emissions price residuals")
    ax.set_xlabel("")
    ax.set_ylabel("Residual")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "eprice_error1_time.pdf")
    plt.close(fig)

    _plot(df[df["year"] > 2004], "lfit2", "eprice_lfit2_time.pdf", "Emissions price fit by bimonth")
    _plot(df[df["year"] > 2004], "lfit3", "eprice_lfit3_time.pdf", "Emissions price fit by quarter")


def main() -> None:
    """
    Run robustness graphs and trend regressions.
    """
    ensure_output_dirs()
    df = load_stata("data_regressions_passthrough.dta")
    df = compute_fits(df)
    generate_graphs(df)

    # Trend regressions (peak vs off-peak), mirroring the Stata robustness block.
    trend_outcomes = run_trend_block(df, include_rd=False)
    note_trend = (
        "Notes: Sample from January 2004 to February 2006, includes all thermal units in the Spanish electricity "
        "market. Only peak hours are included (between 8am and 8pm). All specifications include month of sample, "
        "weekday, and hour-month fixed effects, as well as weather and demand controls "
        "(temperature-month, maximum temperature-month, humidity), supply controls (wind speed and wind speed squared); "
        "and common controls (commodity prices of coal, gas, and oil interacted with hourly fixed effects). The "
        "marginal emissions cost is instrumented with the emissions price. Robust standard errors in parentheses."
    )
    _generic_table(
        trend_outcomes,
        [("ecost2_peak", "Mg. Emissions Costs - Peak"), ("ecost2_off", "Mg. Emissions Costs - Off Peak")],
        TABLE_DIR / "table_cost_pt_trends.tex",
        "Cost Pass-through Regression with Trends",
        "tab:cost_pt_trends",
        note_trend,
    )
    trend_rd_outcomes = run_trend_block(df, include_rd=True)
    note_trend_rd = (
        "Notes: Sample from January 2004 to June 2007, includes all thermal units in the Spanish electricity "
        "market. Only peak hours are included (between 8am and 8pm). All specifications include month of sample, "
        "weekday, and hour-month fixed effects, as well as weather and demand controls "
        "(temperature-month, maximum temperature-month, humidity), supply controls (wind speed and wind speed squared); "
        "and common controls (commodity prices of coal, gas, and oil interacted with hourly fixed effects). The "
        "marginal emissions cost is instrumented with the emissions price. Robust standard errors in parentheses."
    )
    _generic_table(
        trend_rd_outcomes,
        [("ecost2_peak", "Mg. Emissions Costs - Peak"), ("ecost2_off", "Mg. Emissions Costs - Off Peak")],
        TABLE_DIR / "table_cost_pt_trends_rd.tex",
        "Cost Pass-through Regression with Trends including Royal Decree Period",
        "tab:cost_pt_trends_rd",
        note_trend_rd,
    )


if __name__ == "__main__":
    main()
