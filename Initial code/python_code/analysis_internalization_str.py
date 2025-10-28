from __future__ import annotations

import pandas as pd

from utils import (
    add_categorical_dummies,
    fit_iv_2sls,
    fit_ols,
    latex_table,
    load_stata,
    sanitize_cols,
    setup,
    write_text,
)


def _seasonality_cols(df: pd.DataFrame) -> list[str]:
    cols = []
    cols += [c for c in df.columns if c.startswith("summer")]  # summer, summerw
    cols += [c for c in df.columns if c.startswith("spring")]  # spring, springw
    cols += [c for c in df.columns if c.startswith("winter")]  # winter, winterw
    if "weekdays" in df.columns:
        cols.append("weekdays")
    return list(dict.fromkeys(cols))  # unique, preserve order


def run_internalization_table(df: pd.DataFrame):
    # Instruments used for markup in Spec 4
    instruments = ["temp", "windx", "humid", "temperatura"]

    # Common FE: unit dummies (up)
    up_fe = add_categorical_dummies(df, ["up"], drop_first=True)
    seas = _seasonality_cols(df)

    results_all = {}
    # Spec 1: pricehat ~ mg_cost + cost_CO2 (no constant), cluster(id)
    X1 = df[["mg_cost", "cost_CO2"]].copy()
    res1 = fit_ols(df["pricehat"], X1, robust=False, clusters=df.get("id"))
    results_all[1] = res1

    # Spec 2: + unit FE
    X2 = pd.concat([X1, up_fe], axis=1)
    res2 = fit_ols(df["pricehat"], X2, robust=False, clusters=df.get("id"))
    results_all[2] = res2

    # Spec 3: + seasonality controls
    X3 = pd.concat([X2, df[seas]], axis=1)
    res3 = fit_ols(df["pricehat"], X3, robust=False, clusters=df.get("id"))
    results_all[3] = res3

    # Spec 4: price ~ mg_cost + cost_CO2 + (markup endogenous), + seasonality + unit FE
    exog4 = pd.concat([df[["mg_cost", "cost_CO2"]], df[seas], up_fe], axis=1)
    endog4 = df[["markup"]].copy()
    instr4 = df[instruments].copy()
    res4 = fit_iv_2sls(df["price"], exog4, endog4, instr4, robust=True, clusters=df.get("id"))
    results_all[4] = res4

    # Per-firm specs
    results_firm = {1: {}, 2: {}, 3: {}, 4: {}}
    for f in range(1, 5):
        d = df[df["firm_code"] == f].copy()
        if d.empty:
            continue
        up_fe_f = add_categorical_dummies(d, ["up"], drop_first=True)
        X1f = d[["mg_cost", "cost_CO2"]].copy()
        results_firm[f][1] = fit_ols(d["pricehat"], X1f, robust=False, clusters=d.get("id"))
        X2f = pd.concat([X1f, up_fe_f], axis=1)
        results_firm[f][2] = fit_ols(d["pricehat"], X2f, robust=False, clusters=d.get("id"))
        X3f = pd.concat([X2f, d[seas]], axis=1)
        results_firm[f][3] = fit_ols(d["pricehat"], X3f, robust=False, clusters=d.get("id"))
        exog4f = pd.concat([d[["mg_cost", "cost_CO2"]], d[seas], up_fe_f], axis=1)
        endog4f = d[["markup"]].copy()
        instr4f = d[instruments].copy()
        results_firm[f][4] = fit_iv_2sls(d["price"], exog4f, endog4f, instr4f, robust=True, clusters=d.get("id"))

    # Compose LaTeX similar to Stata
    header = " & \\textbf{All} & \\textbf{Firm 1} & \\textbf{Firm 2} & \\textbf{Firm 3} & \\textbf{Firm 4}"
    rows = []

    def fmt_block(title: str, key: str, specs=(1, 2, 3, 4)):
        for s in specs:
            name = {1: "No FE", 2: "Unit FE", 3: "Unit FE + Season", 4: "Spec.3 + Markup (IV)"}[s]
            # coefficients
            cells = [f"({s}) {name}"]
            cells.append(f" {results_all[s].params.get(key, float('nan')):0.3f} ")
            for f in range(1, 5):
                v = results_firm[f][s].params.get(key, float('nan')) if f in results_firm else float('nan')
                cells.append(f" {v:0.3f} ")
            rows.append(cells)
            # std errors
            cells = [" "]
            cells.append(f" ({results_all[s].bse.get(key, float('nan')):0.3f}) ")
            for f in range(1, 5):
                se = results_firm[f][s].bse.get(key, float('nan')) if f in results_firm else float('nan')
                cells.append(f" ({se:0.3f}) ")
            rows.append(cells)

    # Emissions cost (gamma)
    fmt_block("Emissions cost ($\\gamma$)", key="cost_CO2")
    # Input cost (beta)
    fmt_block("Input cost ($\\beta$)", key="mg_cost")
    # Markup (theta) only for Spec 4
    fmt_block("Markup ($\\theta$)", key="markup", specs=(4,))

    # Observations (from spec1)
    cells = ["Obs.", f" {results_all[1].nobs:,.0f} "]
    for f in range(1, 5):
        n = results_firm[f][1].nobs if f in results_firm and 1 in results_firm[f] else 0
        cells.append(f" {n:,.0f} ")
    rows.append(cells)

    tex = latex_table(header, rows,
                      caption="Test based on structural equations",
                      label="tab:intern_structural")
    write_text("table_internalization.tex", tex)


def run_internalization_se_tables(df: pd.DataFrame):
    # Cluster variants for: id, robust, firmday, firmym
    up_fe = add_categorical_dummies(df, ["up"], drop_first=True)
    X = pd.concat([df[["mg_cost", "cost_CO2"]], up_fe], axis=1)

    variants = [
        ("Unit-Level Clusters", df.get("id")),
        ("Robust Std. Errors", None),
        ("Firm-Day Clusters", df.get("firmday")),
        ("Firm-Month Clusters", df.get("firmym")),
    ]

    res_all = []
    for name, grp in variants:
        res_all.append((name, fit_ols(df["pricehat"], X, robust=(grp is None), clusters=grp)))

    # Per-firm
    res_firm = {1: [], 2: [], 3: [], 4: []}
    for f in range(1, 5):
        d = df[df["firm_code"] == f]
        if d.empty:
            continue
        up_fe_f = add_categorical_dummies(d, ["up"], drop_first=True)
        Xf = pd.concat([d[["mg_cost", "cost_CO2"]], up_fe_f], axis=1)
        for name, grp in variants:
            grp_series = d.get(grp.name) if isinstance(grp, pd.Series) else None
            res_firm[f].append((name, fit_ols(d["pricehat"], Xf, robust=(grp_series is None), clusters=grp_series)))

    # LaTeX table (focus on SE presentation similar to Stata)
    header = " & \\textbf{All} & \\textbf{Firm 1} & \\textbf{Firm 2} & \\textbf{Firm 3} & \\textbf{Firm 4}"
    rows = []

    # Coefficients (cost_CO2) top row
    cells = ["Emissions cost ($\\gamma$)", f" {res_all[0][1].params.get('cost_CO2', float('nan')):0.3f} "]
    for f in range(1, 5):
        coeff = res_firm[f][0][1].params.get('cost_CO2', float('nan')) if res_firm.get(f) else float('nan')
        cells.append(f" {coeff:0.3f} ")
    rows.append(cells)

    for idx, (name, r_all) in enumerate(res_all, start=1):
        cells = [f"({idx}) {name}", f" ({r_all.bse.get('cost_CO2', float('nan')):0.3f}) "]
        for f in range(1, 5):
            rf = res_firm[f][idx - 1][1] if res_firm.get(f) else None
            se = rf.bse.get('cost_CO2', float('nan')) if rf is not None else float('nan')
            cells.append(f" ({se:0.3f}) ")
        rows.append(cells)

    # Input cost block
    cells = ["Input cost ($\\beta$)", f" {res_all[0][1].params.get('mg_cost', float('nan')):0.3f} "]
    for f in range(1, 5):
        coeff = res_firm[f][0][1].params.get('mg_cost', float('nan')) if res_firm.get(f) else float('nan')
        cells.append(f" {coeff:0.3f} ")
    rows.append(cells)

    for idx, (name, r_all) in enumerate(res_all, start=1):
        cells = [f"({idx}) {name}", f" ({r_all.bse.get('mg_cost', float('nan')):0.3f}) "]
        for f in range(1, 5):
            rf = res_firm[f][idx - 1][1] if res_firm.get(f) else None
            se = rf.bse.get('mg_cost', float('nan')) if rf is not None else float('nan')
            cells.append(f" ({se:0.3f}) ")
        rows.append(cells)

    tex = latex_table(header, rows,
                      caption="Test based on structural equations -- Effects of Clustering",
                      label="tab:intern_structural_stderrors")
    write_text("table_internalization_stderrors.tex", tex)


def main():
    setup()
    df = load_stata("data_regressions_structural.dta")
    df = sanitize_cols(df)
    run_internalization_table(df)
    run_internalization_se_tables(df)


if __name__ == "__main__":
    main()

