from __future__ import annotations

import numpy as np
import pandas as pd

from utils import (
    add_categorical_dummies,
    add_interaction_with_continuous,
    fit_iv_2sls,
    latex_table,
    load_stata,
    sanitize_cols,
    setup,
    write_text,
)


def _base_matrices(df: pd.DataFrame) -> pd.DataFrame:
    # controls1: hour#(coal gas brent) + linear coal gas brent
    # Implement via hour dummies interacted with each price series
    hd = add_categorical_dummies(df, ["hour"], drop_first=True)
    inter = []
    for v in ["coal", "gas", "brent"]:
        d = hd.add_prefix(f"hourX{v}_")
        for c in d.columns:
            d[c] = d[c] * df[v].values
        inter.append(d)
    controls1 = pd.concat(inter + [df[["coal", "gas", "brent"]]], axis=1)

    # base FE
    fe = pd.concat([
        add_categorical_dummies(df, ["hour"], drop_first=True),
        add_categorical_dummies(df, ["year"], drop_first=True),
        add_categorical_dummies(df, ["weekd"], drop_first=True),
        add_categorical_dummies(df, ["month"], drop_first=True),
    ], axis=1)

    # Month×Hour FE and Month×Temp interactions
    mon_hour = add_categorical_dummies(pd.DataFrame({
        "monhour": df["month"].astype(str) + ":" + df["hour"].astype(str)
    }), ["monhour"], drop_first=True, prefix="monXhou")
    mon_temp = add_interaction_with_continuous(df, "month", "temp", prefix="monXtem")
    mon_tempx = add_interaction_with_continuous(df, "month", "tempx", prefix="monXtemx")

    X = pd.concat([controls1, fe, mon_hour, mon_temp, mon_tempx], axis=1)
    return sanitize_cols(X)


def _add_time_trends(df: pd.DataFrame, X: pd.DataFrame, group: str) -> pd.DataFrame:
    # group in {"ym", "yb", "yq"}; add dummies for group and their interaction with time
    dummies = add_categorical_dummies(df, [group], drop_first=True)
    inter = dummies.copy()
    for c in inter.columns:
        inter[c] = inter[c] * df["time"].values
    inter = inter.add_prefix(f"{group}Xt_")
    return pd.concat([X, dummies, inter], axis=1)


def run_robustness_tables(df: pd.DataFrame, include_rd: bool, outname: str, caption: str, label: str):
    data = df.copy()
    if not include_rd:
        data = data[data["rd"] == 0]

    # Ensure `time` exists as integer index for linear trends
    if "time" not in data.columns:
        data["time"] = data.groupby(["year", "month", "day"])['day'].transform('size')
        data["time"] = pd.factorize(list(zip(data.year, data.month, data.day)))[0] + 1

    X_base = _base_matrices(data)

    specs = {}
    for i, grp in enumerate([None, "ym", "yb", "yq"], start=1):
        X = X_base if grp is None else _add_time_trends(data, X_base, grp)
        endog = data[["ecost2_peak", "ecost2_off"]]
        instr = data[["eprice"]].copy()
        if "peak" in data.columns:
            instr = pd.concat([instr, (data["peak"] * data["eprice"]).rename("peakXeprice")], axis=1)
        res = fit_iv_2sls(data["mg_price"], X, endog, instr, robust=True)
        specs[i] = res

    header = " & \\textbf{(1)} & \\textbf{(2)} & \\textbf{(3)} & \\textbf{(4)}"
    rows = []

    def fmt_row(name: str, key: str):
        cells = [name]
        for i in range(1, 5):
            coef = specs[i].params.get(key, float('nan'))
            cells.append(f" {coef:0.3f} ")
        rows.append(cells)
        cells = [" "]
        for i in range(1, 5):
            se = specs[i].bse.get(key, float('nan'))
            cells.append(f" ({se:0.3f}) ")
        rows.append(cells)

    fmt_row("Mg. Emissions Costs - Peak", "ecost2_peak")
    fmt_row("Mg. Emissions Costs - Off Peak", "ecost2_off")

    tex = latex_table(header, rows, caption=caption, label=label)
    write_text(outname, tex)


def main():
    setup()
    df = load_stata("data_regressions_passthrough.dta")
    # Precompute grouping variables as in Stata
    df = df.copy()
    df["quarter"] = ((df["month"] - 1) // 3) + 1
    df["bimonth"] = np.ceil(df["month"] / 2).astype(int)
    df["ym"] = df["year"].astype(str) + ":" + df["month"].astype(str)
    df["yb"] = df["year"].astype(str) + ":" + df["bimonth"].astype(str)
    df["yq"] = df["year"].astype(str) + ":Q" + df["quarter"].astype(str)

    run_robustness_tables(
        df,
        include_rd=False,
        outname="table_cost_pt_trends.tex",
        caption="Cost Pass-through Regression with Trends",
        label="tab:cost_pt_trends",
    )
    run_robustness_tables(
        df,
        include_rd=True,
        outname="table_cost_pt_trends_rd.tex",
        caption="Cost Pass-through Regression with Trends including Royal Decree Period",
        label="tab:cost_pt_trends_rd",
    )


if __name__ == "__main__":
    main()
