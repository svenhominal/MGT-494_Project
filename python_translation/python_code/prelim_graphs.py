"""
Replicate Stata's `prelim_graphs.do` to produce price and emissions rate figures.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from statsmodels.nonparametric.kernel_regression import KernelReg

from utils import DATA_DIR, FIG_DIR, ensure_output_dirs, load_stata


np.random.seed(42)


def _collapse_prices(df: pd.DataFrame) -> pd.DataFrame:
    """
    Collapse daily prices to mean/max/min as in Stata's `collapse`.
    """
    # grouped = (
    #     df.groupby(["year", "month", "day"], as_index=False)
    #     .agg(
    #         {
    #             "eprice": "mean",
    #             "mg_price": "mean",
    #             "mg_price": ["max", "min"],
    #         }
    #     )
    #     .copy()
    # )
    grouped = (
    df.groupby(["year", "month", "day"], as_index=False)
      .agg(
          eprice_mean=("eprice", "mean"),
          mg_price_mean=("mg_price", "mean"),
          mg_price_max=("mg_price", "max"),
          mg_price_min=("mg_price", "min"),
      )
      .copy()
    )
    # print(grouped.head())
    # Flatten multi-index columns created by the agg above.
    grouped.columns = ["year", "month", "day", "eprice", "mg_price", "max_price", "min_price"]
    # grouped.columns = ["year", "month", "day", "eprice", "max_price", "min_price"]
    grouped["time"] = pd.to_datetime(dict(year=grouped.year, month=grouped.month, day=grouped.day))
    return grouped


def _local_poly_ci(
    x: np.ndarray,
    y: np.ndarray,
    grid: np.ndarray,
    bandwidth: float = 0.3,
    n_boot: int = 200,
    seed: int = 123,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Local-linear smoother with bootstrap CIs to mimic Stata's lpolyci.
    """
    kr = KernelReg(endog=y, exog=x, var_type="c", reg_type="ll", bw=[bandwidth])
    mean_fit, _ = kr.fit(grid)

    rng = np.random.default_rng(seed)
    boot_draws = np.empty((n_boot, grid.size))
    for b in range(n_boot):
        sample_idx = rng.integers(0, len(y), len(y))
        yb = y[sample_idx]
        xb = x[sample_idx]
        kr_b = KernelReg(endog=yb, exog=xb, var_type="c", reg_type="ll", bw=[bandwidth])
        boot_draws[b], _ = kr_b.fit(grid)
    se = boot_draws.std(axis=0)
    ci_low = mean_fit - 1.96 * se
    ci_high = mean_fit + 1.96 * se
    return mean_fit, ci_low, ci_high


def plot_prices(df: pd.DataFrame, output_dir: Path) -> None:
    """
    Plot emissions and marginal electricity prices over time for the reduced sample.
    """
    df = df.loc[
        (df["year"] >= 2004)
        & ((df["year"] < 2007) | ((df["year"] == 2007) & (df["month"] <= 6))),
        ["year", "month", "day", "eprice", "mg_price"],
    ].drop_duplicates()
    # print(df.head())
    collapsed = _collapse_prices(df)
    mask_reduced = (collapsed["year"] < 2006) | (
        (collapsed["year"] == 2006) & (collapsed["month"] < 3)
    )
    reduced = collapsed.loc[mask_reduced].sort_values("time")

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(reduced["time"], reduced["mg_price"], label="Daily Electricity Price (€/MWh)")
    ax.plot(reduced["time"], reduced["eprice"], label="Emissions Price (€/ton)")
    ax.set_ylabel("Euros")
    ax.set_xlabel("")
    ax.legend()
    ax.set_title("")
    fig.tight_layout()

    output_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_dir / "prices_sample_reduced.pdf")
    fig.savefig(output_dir / "prices_sample_reduced.eps")
    plt.grid()
    plt.close(fig)


def plot_erate(df: pd.DataFrame, output_dir: Path) -> None:
    """
    Plot marginal emissions rate vs. hour with local polynomial fit and CI.
    """
    df = df.loc[
        # (df["year"] <= 2006) & ~((df["year"] == 2006) & (df["month"] > 2)),
        (df.year < 2006) | ((df.year == 2006) & (df.month <= 2)),
        ["hour", "erate", "year", "month", "day"],
    ].drop_duplicates().dropna()
    # print(df.head())
    hours = df["hour"].to_numpy()
    erate = df["erate"].to_numpy()
    grid = np.arange(hours.min(), hours.max() + 1)
    # mean_fit, ci_low, ci_high = _local_poly_ci(hours, erate, grid, bandwidth=1.0)
    # print(f"Mean fit: {mean_fit}\nci_low: {ci_low}\nci_high: {ci_high}")

    gr = df.groupby("hour")["erate"]
    stats = gr.agg(["mean", "count", "std"]).reset_index()
    stats["se"] = stats["std"] / stats["count"].pow(0.5)
    stats["lower"] = stats["mean"] - 1.96 * stats["se"]
    stats["upper"] = stats["mean"] + 1.96 * stats["se"]


    fig, ax = plt.subplots(figsize=(8, 4))
    # ax.fill_between(grid, ci_low, ci_high, alpha=0.2, label="CI 95%")
    # ax.plot(grid, mean_fit, label="Emissions Rate")
    ax.fill_between(stats["hour"], stats["lower"], stats["upper"], color="#cfe2f3", label="CI 95%")
    ax.plot(stats["hour"], stats["mean"], color="#2166ac", label="Emissions Rate")
    ax.set_xlabel("Hour of the Day")
    ax.set_ylabel("Emissions Rate (Tons CO2/MWh)")
    ax.set_xticks(grid)
    ax.legend()
    fig.tight_layout()

    output_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_dir / "erate_hour.pdf")
    fig.savefig(output_dir / "erate_hour.eps")
    plt.grid()
    plt.close(fig)


def main() -> None:
    """
    Run the two summary plots generated by the Stata code.
    """
    ensure_output_dirs()
    df = load_stata("data_regressions_passthrough.dta")
    plot_prices(df, FIG_DIR)
    plot_erate(df, FIG_DIR)


if __name__ == "__main__":
    main()
