from __future__ import annotations

import pandas as pd

from utils import (
    add_categorical_dummies,
    add_interaction_with_continuous,
    fit_iv_2sls,
    load_stata,
    sanitize_cols,
    setup,
    write_text,
    latex_table,
)


def _build_common_and_fe(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    demandcontrols = ["temp", "tempx", "humid"]
    supplycontrols = ["windx", "windx2"]
    controls = ["coal", "gas", "brent"]

    X_common = df[demandcontrols + supplycontrols + controls].copy()
    # Base fixed effects: hour, year, weekd, month
    fe = {
        "hour": add_categorical_dummies(df, ["hour"], drop_first=True),
        "year": add_categorical_dummies(df, ["year"], drop_first=True),
        "weekd": add_categorical_dummies(df, ["weekd"], drop_first=True),
        "month": add_categorical_dummies(df, ["month"], drop_first=True),
    }
    return X_common, fe


def _month_year_fe(df: pd.DataFrame) -> pd.DataFrame:
    my = df["month"].astype(str) + ":" + df["year"].astype(str)
    return add_categorical_dummies(pd.DataFrame({"monyear": my}), ["monyear"], drop_first=True, prefix="monXyea")


def _month_hour_fe(df: pd.DataFrame) -> pd.DataFrame:
    mh = df["month"].astype(str) + ":" + df["hour"].astype(str)
    return add_categorical_dummies(pd.DataFrame({"monhour": mh}), ["monhour"], drop_first=True, prefix="monXhou")


def _hour_x_inputs(df: pd.DataFrame) -> pd.DataFrame:
    # Interactions hour dummies with coal, gas, brent
    hd = add_categorical_dummies(df, ["hour"], drop_first=True)
    out = []
    for v in ["coal", "gas", "brent"]:
        d = hd.add_prefix(f"hourX{v}_")
        for c in d.columns:
            d[c] = d[c] * df[v].values
        out.append(d)
    return pd.concat(out, axis=1)


def _build_spec_matrix(df: pd.DataFrame, spec: int) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Return (exog, endog, instruments) for given spec (1..5)."""
    X_common, fe = _build_common_and_fe(df)

    # Base FE
    X = pd.concat([X_common, fe["hour"], fe["year"], fe["weekd"], fe["month"]], axis=1)

    # Month×Year FE (as in _ImonXyea*)
    X = pd.concat([X, _month_year_fe(df)], axis=1)

    # Add spec-specific terms
    if spec in (2, 4, 5):
        # Month×Temp and Month×Tempx
        X = pd.concat([X,
                       add_interaction_with_continuous(df, "month", "temp", prefix="monXtem"),
                       add_interaction_with_continuous(df, "month", "tempx", prefix="monXtemx")], axis=1)
    if spec in (3, 4, 5):
        # Month×Hour FE
        X = pd.concat([X, _month_hour_fe(df)], axis=1)
    if spec == 5:
        # Hour×(coal, gas, brent)
        X = pd.concat([X, _hour_x_inputs(df)], axis=1)

    endog = df[["ecost2"]].copy()
    instr = df[["eprice"]].copy()
    return sanitize_cols(X), sanitize_cols(endog), sanitize_cols(instr)


def run_baseline_tables(df: pd.DataFrame):
    # Drop Royal Decree period (rd == 1)
    data = df.copy()
    data = data[data["rd"] != 1]

    specs = {}
    for i in range(1, 6):
        X, endog, Z = _build_spec_matrix(data, i)
        res = fit_iv_2sls(y=data["mg_price"], exog=X, endog=endog, instruments=Z, robust=True)
        specs[i] = res

    # Build LaTeX similar to Stata's table_cost_pt_base.tex
    header = " & \\textbf{(1)} & \\textbf{(2)} & \\textbf{(3)} & \\textbf{(4)} & \\textbf{(5)}"
    rows = []

    def fmt_row(name: str, key: str) -> None:
        # coefficients
        cells = [name]
        for i in range(1, 6):
            coef = specs[i].params.get(key, float('nan'))
            cells.append(f" {coef:0.3f} ")
        rows.append(cells)
        # std errors
        cells = [" "]
        for i in range(1, 6):
            se = specs[i].bse.get(key, float('nan'))
            cells.append(f" ({se:0.3f}) ")
        rows.append(cells)

    fmt_row("Mg. Emissions Costs $(\\rho)$", "ecost2")
    rows.append(["\\hline"])  # horizontal line

    # Optional: show wind and wind^2, coal/gas/brent where available
    for nm, key in [("Wind Speed", "windx"), ("Wind Speed Squared", "windx2"),
                    ("Coal", "coal"), ("Gas", "gas"), ("Brent", "brent")]:
        fmt_row(nm, key)

    # First-stage F (if available)
    cells = ["F-test"]
    for i in range(1, 6):
        fval = specs[i].f_first_stage
        cells.append("" if fval is None else f" {fval:0.1f} ")
    rows.append(cells)

    tex = latex_table(header, rows,
                      caption="Cost Pass-through Regression Results",
                      label="tab:cost_pt")
    write_text("table_cost_pt_base.tex", tex)


def run_peak_tables(df: pd.DataFrame):
    # Peak/off-peak specification with two endogenous variables (ecost2_peak, ecost2_off)
    data = df.copy()
    data = data[data["rd"] != 1]

    specs = {}
    for i in range(1, 6):
        X, _, Z = _build_spec_matrix(data, i)
        endog = data[["ecost2_peak", "ecost2_off"]].copy()
        instr = data[["eprice"]].copy()
        # include peak×eprice as additional instrument
        if "peak" in data.columns:
            instr = pd.concat([instr, (data["peak"] * data["eprice"]).rename("peakXeprice")], axis=1)
        res = fit_iv_2sls(y=data["mg_price"], exog=X, endog=endog, instruments=instr, robust=True)
        specs[i] = res

    header = " & \\textbf{(1)} & \\textbf{(2)} & \\textbf{(3)} & \\textbf{(4)} & \\textbf{(5)}"
    rows = []

    def fmt_row(name: str, key: str) -> None:
        cells = [name]
        for i in range(1, 6):
            coef = specs[i].params.get(key, float('nan'))
            cells.append(f" {coef:0.3f} ")
        rows.append(cells)
        cells = [" "]
        for i in range(1, 6):
            se = specs[i].bse.get(key, float('nan'))
            cells.append(f" ({se:0.3f}) ")
        rows.append(cells)

    fmt_row("Mg. Emissions Costs - Peak", "ecost2_peak")
    fmt_row("Mg. Emissions Costs - Off Peak", "ecost2_off")

    tex = latex_table(header, rows,
                      caption="Cost Pass-through Regression Results: Peak vs. Non-Peak",
                      label="tab:cost_pt_peak")
    write_text("table_cost_pt_peak.tex", tex)


def main():
    setup()
    df = load_stata("data_regressions_passthrough.dta")
    run_baseline_tables(df)
    run_peak_tables(df)


if __name__ == "__main__":
    main()

