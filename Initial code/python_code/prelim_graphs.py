from __future__ import annotations

import datetime as dt

import matplotlib.pyplot as plt
import pandas as pd

from config import FIGURES_DIR
from utils import load_stata, save_figure, setup


def plot_prices_sample_reduced():
    df = load_stata("data_regressions_passthrough.dta")
    cols = ["year", "month", "day", "eprice", "mg_price"]
    df = df[cols].drop_duplicates()
    df = df[(df["year"] >= 2004) & ((df["year"] < 2007) | ((df["year"] == 2007) & (df["month"] <= 6)))]
    # collapse by day (mean)
    g = df.groupby(["year", "month", "day"]).agg({"eprice": "mean", "mg_price": "mean"}).reset_index()
    g["time"] = pd.to_datetime(dict(year=g.year, month=g.month, day=g.day))

    reduced = (g[(g.year < 2006) | ((g.year == 2006) & (g.month < 3))]).copy()

    fig, ax = plt.subplots(figsize=(10, 3))
    ax.plot(reduced["time"], reduced["eprice"], label="Emissions Price (€/ton)")
    ax.plot(reduced["time"], reduced["mg_price"], label="Daily Electricity Price (€/MWh)")
    ax.set_ylabel("Euros")
    ax.set_xlabel("")
    ax.legend()
    ax.grid(True, alpha=0.2)
    fig.tight_layout()

    p_pdf = save_figure("prices_sample_reduced.pdf")
    p_eps = save_figure("prices_sample_reduced.eps")
    fig.savefig(p_pdf)
    fig.savefig(p_eps)
    plt.close(fig)


def plot_erate_hour_ci():
    df = load_stata("data_regressions_passthrough.dta")
    cols = ["year", "month", "day", "hour", "erate"]
    df = df[cols].drop_duplicates()
    df = df[(df.year < 2006) | ((df.year == 2006) & (df.month <= 2))]

    # Approximate lpolyci by hourly mean with 95% CI (normal approx)
    gr = df.groupby("hour")["erate"]
    stats = gr.agg(["mean", "count", "std"]).reset_index()
    stats["se"] = stats["std"] / stats["count"].pow(0.5)
    stats["lower"] = stats["mean"] - 1.96 * stats["se"]
    stats["upper"] = stats["mean"] + 1.96 * stats["se"]

    fig, ax = plt.subplots(figsize=(8, 3))
    ax.fill_between(stats["hour"], stats["lower"], stats["upper"], color="#cfe2f3", label="CI 95%")
    ax.plot(stats["hour"], stats["mean"], color="#2166ac", label="Emissions Rate")
    ax.set_ylabel("Emissions Rate (Tons CO₂/MWh)")
    ax.set_xlabel("Hour of the Day")
    ax.set_xticks(list(range(1, 25)))
    ax.grid(True, alpha=0.2)
    ax.legend()
    fig.tight_layout()

    p_pdf = save_figure("erate_hour.pdf")
    p_eps = save_figure("erate_hour.eps")
    fig.savefig(p_pdf)
    fig.savefig(p_eps)
    plt.close(fig)


def main():
    setup()
    plot_prices_sample_reduced()
    plot_erate_hour_ci()


if __name__ == "__main__":
    main()

