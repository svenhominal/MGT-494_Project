"""
Translation of `analysis_internalization_str.do` to Python.

Runs structural internalization regressions with clustered standard errors
and writes LaTeX tables mirroring the Stata outputs.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from linearmodels.iv import IV2SLS

from utils import TABLE_DIR, ensure_output_dirs, fmt, load_stata, run_iv, write_text


np.random.seed(42)


@dataclass
class FittedModel:
    """
    Container for OLS/IV model results and metadata.
    """

    name: str
    result: object
    dep: str
    cluster: Optional[str] = None


INSTRUMENTS = ["temp", "windx", "humid", "temperatura"]
SEASONAL_TOKENS = ["summer*", "spring*", "winter*", "weekdays"]


def _expand_terms(df: pd.DataFrame, tokens: Sequence[str]) -> List[str]:
    """
    Expand Stata-style wildcard terms (e.g., summer*) using dataframe columns.
    """
    expanded: List[str] = []
    for tok in tokens:
        if tok.endswith("*"):
            prefix = tok[:-1]
            expanded.extend([col for col in df.columns if col.startswith(prefix)])
        else:
            expanded.append(tok)
    return expanded


def _fit_ols(
    df: pd.DataFrame,
    dep: str,
    exog: Sequence[str],
    cov: str,
    cluster_var: Optional[str],
    include_const: bool = True,
) -> smf.ols:
    """
    Fit an OLS model with optional clustering.
    """
    const_term = "-1" if not include_const else "1"
    formula = f"{dep} ~ {const_term} + " + " + ".join(exog)
    cov_kwds = None
    cov_type = "nonrobust"
    if cov == "robust":
        cov_type = "HC1"
    elif cov == "cluster" and cluster_var is not None:
        cov_type = "cluster"
        cov_kwds = {"groups": df[cluster_var]}
    return smf.ols(formula, data=df).fit(cov_type=cov_type, cov_kwds=cov_kwds)


def _fit_iv(
    df: pd.DataFrame,
    dep: str,
    exog: Sequence[str],
    endog: Sequence[str],
    instruments: Sequence[str],
    cov: str,
    cluster_var: Optional[str],
    include_const: bool = True,
) -> IV2SLS:
    """
    Fit an IV regression using linearmodels with robust or clustered covariance.
    """
    clusters = df[cluster_var] if cov == "cluster" and cluster_var is not None else None
    cov_type = "robust" if cov == "robust" else "clustered"
    return run_iv(
        data=df,
        dep=dep,
        endog=endog,
        instruments=instruments,
        exog=list(exog),
        cov_type=cov_type,
        clusters=clusters,
        include_const=include_const,
    )


def _collect(result, var: str) -> Tuple[Optional[float], Optional[float]]:
    """
    Extract coefficient and standard error from a statsmodels or linearmodels result.
    """
    try:
        beta = float(result.params[var])
        se = float(result.bse[var])
        return beta, se
    except KeyError:
        try:
            beta = float(result.params[var])
            se = float(result.std_errors[var])
            return beta, se
        except Exception:
            return None, None


def _clean_data(df: pd.DataFrame, cols: Sequence[str]) -> pd.DataFrame:
    """
    Drop observations with missing values in required columns.
    """
    return df.dropna(subset=list(set(cols)))


def run_main_specs(df: pd.DataFrame) -> Dict[str, FittedModel]:
    """
    Run the four baseline structural internalization specifications.
    """
    results: Dict[str, FittedModel] = {}
    base_exog = ["mg_cost", "cost_CO2"]
    seasonal = _expand_terms(df, SEASONAL_TOKENS)

    # All units
    data1 = _clean_data(df, base_exog + ["pricehat", "id"])
    res1 = _fit_ols(data1, "pricehat", base_exog, cov="cluster", cluster_var="id", include_const=False)
    results["spec1_all"] = FittedModel(name="spec1_all", result=res1, dep="pricehat", cluster="id")

    data2 = _clean_data(df, base_exog + ["pricehat", "id", "up"])
    res2 = _fit_ols(data2, "pricehat", base_exog + ["C(up)"], cov="cluster", cluster_var="id")
    results["spec2_all"] = FittedModel(name="spec2_all", result=res2, dep="pricehat", cluster="id")

    data3 = _clean_data(df, base_exog + seasonal + ["pricehat", "id", "up"])
    res3 = _fit_ols(
        data3,
        "pricehat",
        base_exog + seasonal + ["C(up)"],
        cov="cluster",
        cluster_var="id",
    )
    results["spec3_all"] = FittedModel(name="spec3_all", result=res3, dep="pricehat", cluster="id")

    data4 = _clean_data(df, base_exog + seasonal + ["price", "id", "up", "markup"] + INSTRUMENTS)
    res4 = _fit_iv(
        data4,
        "price",
        base_exog + seasonal + ["C(up)"],
        endog=["markup"],
        instruments=INSTRUMENTS,
        cov="cluster",
        cluster_var="id",
    )
    results["spec4_all"] = FittedModel(name="spec4_all", result=res4, dep="price", cluster="id")

    for fcode in sorted(df["firm_code"].dropna().unique()):
        subset = df[df["firm_code"] == fcode]
        d1 = _clean_data(subset, base_exog + ["pricehat", "id"])
        res = _fit_ols(d1, "pricehat", base_exog, cov="cluster", cluster_var="id", include_const=False)
        results[f"spec1_f{int(fcode)}"] = FittedModel(name=f"spec1_f{int(fcode)}", result=res, dep="pricehat", cluster="id")

        d2 = _clean_data(subset, base_exog + ["pricehat", "id", "up"])
        res = _fit_ols(d2, "pricehat", base_exog + ["C(up)"], cov="cluster", cluster_var="id")
        results[f"spec2_f{int(fcode)}"] = FittedModel(name=f"spec2_f{int(fcode)}", result=res, dep="pricehat", cluster="id")

        d3 = _clean_data(subset, base_exog + seasonal + ["pricehat", "id", "up"])
        res = _fit_ols(
            d3,
            "pricehat",
            base_exog + seasonal + ["C(up)"],
            cov="cluster",
            cluster_var="id",
        )
        results[f"spec3_f{int(fcode)}"] = FittedModel(name=f"spec3_f{int(fcode)}", result=res, dep="pricehat", cluster="id")

        d4 = _clean_data(subset, base_exog + seasonal + ["price", "id", "up", "markup"] + INSTRUMENTS)
        res = _fit_iv(
            d4,
            "price",
            base_exog + seasonal + ["C(up)"],
            endog=["markup"],
            instruments=INSTRUMENTS,
            cov="cluster",
            cluster_var="id",
        )
        results[f"spec4_f{int(fcode)}"] = FittedModel(name=f"spec4_f{int(fcode)}", result=res, dep="price", cluster="id")
    return results


def run_cluster_effects(df: pd.DataFrame) -> Dict[str, FittedModel]:
    """
    Estimate models with alternative clustering levels for the robustness table.
    """
    results: Dict[str, FittedModel] = {}
    base_exog = ["mg_cost", "cost_CO2", "C(up)"]
    dep = "pricehat"
    for label, cov, cluster in [
        ("spec_sd1", "cluster", "id"),
        ("spec_sd2", "robust", None),
        ("spec_sd3", "cluster", "firmday"),
        ("spec_sd4", "cluster", "firmym"),
    ]:
        cols = base_exog + [dep]
        if cluster:
            cols.append(cluster)
        d = _clean_data(df, cols)
        res = _fit_ols(d, dep, base_exog, cov=cov, cluster_var=cluster)
        results[label] = FittedModel(name=label, result=res, dep=dep, cluster=cluster)
        for fcode in sorted(df["firm_code"].dropna().unique()):
            subset = df[df["firm_code"] == fcode]
            cols_f = base_exog + [dep]
            if cluster:
                cols_f.append(cluster)
            d_f = _clean_data(subset, cols_f)
            res_f = _fit_ols(d_f, dep, base_exog, cov=cov, cluster_var=cluster)
            results[f"{label}_f{int(fcode)}"] = FittedModel(
                name=f"{label}_f{int(fcode)}", result=res_f, dep=dep, cluster=cluster
            )
    return results


def _write_main_table(results: Dict[str, FittedModel], table_path: Path) -> None:
    """
    Build LaTeX table for the main structural regressions.
    """
    spec_names = ["No FE", "Unit FE", "Unit FE + Season", "Spec.3 + Markup (IV)"]
    header = ["", "\\textbf{All}"] + [f"\\textbf{{Firm {i}}}" for i in range(1, 5)]
    rows: List[str] = ["\\begin{tabular*}{.9\\textwidth}{@{\\extracolsep{\\fill}} l c c c c c}", "\\hline\\hline"]
    rows.append(_latex_row(header))
    rows.append("\\cline{2-6} \\\\[-\\sep]")

    # Emissions cost
    rows.append("\\textbf{Emissions cost} ($\\gamma$) \\\\[\\sep]")
    for idx, name in enumerate(spec_names, start=1):
        coef_row = [f"({idx}) {name}"]
        se_row = [""]
        keys = [f"spec{idx}_all"] + [f"spec{idx}_f{i}" for i in range(1, 5)]
        for key in keys:
            beta, se = _collect(results[key].result, "cost_CO2")
            coef_row.append(fmt(beta))
            se_row.append(f"({fmt(se)})")
        rows.append(_latex_row(coef_row))
        rows.append(_latex_row(se_row) + "\\[\\sep]")

    rows.append(" \\hline \\\\[-\\sep]")
    rows.append("\\textbf{Input cost} ($\\beta$) \\\\[\\sep]")
    for idx, name in enumerate(spec_names, start=1):
        coef_row = [f"({idx}) {name}"]
        se_row = [""]
        keys = [f"spec{idx}_all"] + [f"spec{idx}_f{i}" for i in range(1, 5)]
        for key in keys:
            beta, se = _collect(results[key].result, "mg_cost")
            coef_row.append(fmt(beta))
            se_row.append(f"({fmt(se)})")
        rows.append(_latex_row(coef_row))
        rows.append(_latex_row(se_row) + "\\[\\sep]")

    rows.append(" \\hline \\\\[-\\sep]")
    rows.append("\\textbf{Markup} ($\\theta$) \\\\[\\sep]")
    coef_row = ["(4) Spec.3 + Markup (IV)"]
    se_row = [""]
    keys = ["spec4_all"] + [f"spec4_f{i}" for i in range(1, 5)]
    for key in keys:
        beta, se = _collect(results[key].result, "markup")
        coef_row.append(fmt(beta))
        se_row.append(f"({fmt(se)})")
    rows.append(_latex_row(coef_row))
    rows.append(_latex_row(se_row))

    rows.append(" \\hline \\\\[-\\sep]")
    obs_row = ["Obs."]
    keys = ["spec1_all"] + [f"spec1_f{i}" for i in range(1, 5)]
    for key in keys:
        obs_row.append(f"{int(results[key].result.nobs):,}")
    rows.append(_latex_row(obs_row) + " \\\\[\\sep] \\hline \\hline")
    table = [
        "\\begin{table}",
        "\\centering",
        "\\caption{Test based on structural equations} \\label{tab:intern_structural}",
    ]
    table.extend(rows)
    table.append("\\end{tabular*}")
    table.append("\\begin{minipage}[c]{.9\\textwidth}")
    table.append(
        "{\\footnotesize \\vspace{6pt} "
        "Notes: Sample from January 2004 to February 2006, includes all thermal units in the Spanish electricity market. "
        "Standard errors clustered at the unit level.}"
    )
    table.append("\\end{minipage}")
    table.append("\\end{table}")
    write_text(table_path, "\n".join(table))


def _write_cluster_table(results: Dict[str, FittedModel], table_path: Path) -> None:
    """
    Build LaTeX table comparing alternative clustering choices.
    """
    cluster_names = [
        ("spec_sd1", "Unit-Level Clusters"),
        ("spec_sd2", "Robust Std. Errors"),
        ("spec_sd3", "Firm-Day Clusters"),
        ("spec_sd4", "Firm-Month Clusters"),
    ]
    header = ["", "\\textbf{All}"] + [f"\\textbf{{Firm {i}}}" for i in range(1, 5)]
    rows = ["\\begin{tabular*}{.9\\textwidth}{@{\\extracolsep{\\fill}} l c c c c c}", "\\hline\\hline"]
    rows.append(_latex_row(header))
    rows.append("\\cline{2-6} \\\\[-\\sep]")
    rows.append("\\textbf{Emissions cost} ($\\gamma$)")
    coef_row = [""]
    keys = ["spec_sd1"] + [f"spec_sd1_f{i}" for i in range(1, 5)]
    for key in keys:
        beta, _ = _collect(results[key].result, "cost_CO2")
        coef_row.append(fmt(beta))
    rows.append(_latex_row(coef_row) + " \\\\[\\sep]")
    for idx, (key_base, label) in enumerate(cluster_names, start=1):
        se_row = [f"({idx}) {label}"]
        for key in [key_base] + [f"{key_base}_f{i}" for i in range(1, 5)]:
            _, se = _collect(results[key].result, "cost_CO2")
            se_row.append(f"({fmt(se)})")
        rows.append(_latex_row(se_row))
    rows.append(" \\hline \\\\[-\\sep]")
    rows.append("\\textbf{Input cost} ($\\beta$)")
    coef_row = [""]
    for key in keys:
        beta, _ = _collect(results[key].result, "mg_cost")
        coef_row.append(fmt(beta))
    rows.append(_latex_row(coef_row) + " \\\\[\\sep]")
    for idx, (key_base, label) in enumerate(cluster_names, start=1):
        se_row = [f"({idx}) {label}"]
        for key in [key_base] + [f"{key_base}_f{i}" for i in range(1, 5)]:
            _, se = _collect(results[key].result, "mg_cost")
            se_row.append(f"({fmt(se)})")
        rows.append(_latex_row(se_row))
    rows.append(" \\hline \\\\[-\\sep]")
    obs_row = ["Obs."] + [f"{int(results[key].result.nobs):,}" for key in keys]
    rows.append(_latex_row(obs_row) + " \\\\[\\sep] \\hline \\hline")

    table = [
        "\\begin{table}",
        "\\centering",
        "\\caption{Test based on structural equations -- Effects of Clustering} \\label{tab:intern_structural_stderrors}",
    ]
    table.extend(rows)
    table.append("\\end{tabular*}")
    table.append("\\begin{minipage}[c]{.9\\textwidth}")
    table.append(
        "{\\footnotesize \\vspace{6pt} "
        "Notes: Sample from January 2004 to February 2006, includes all thermal units in the Spanish electricity market. "
        "Regression includes unit fixed effects. Each row considers a different level of clustering: unit-level clusters "
        "(our baseline specification), robust White standard errors, firm-day clusters to account for correlation in "
        "bidding within a firm at a given day, and firm-month of sample clusters to account for longer temporal clustering. }"
    )
    table.append("\\end{minipage}")
    table.append("\\end{table}")
    write_text(table_path, "\n".join(table))


def main() -> None:
    """
    Run structural internalization regressions and write output tables/logs.
    """
    ensure_output_dirs()
    df = load_stata("data_regressions_structural.dta")

    main_results = run_main_specs(df)
    log_main = []
    for key, model in main_results.items():
        log_main.append(f"== {key} ==")
        log_main.append(str(model.result.summary()))
    write_text(TABLE_DIR / "table_internalization.log", "\n\n".join(log_main))
    _write_main_table(main_results, TABLE_DIR / "table_internalization.tex")

    cluster_results = run_cluster_effects(df)
    log_sd = []
    for key, model in cluster_results.items():
        log_sd.append(f"== {key} ==")
        log_sd.append(str(model.result.summary()))
    write_text(TABLE_DIR / "table_internalization_stderrors.log", "\n\n".join(log_sd))
    _write_cluster_table(cluster_results, TABLE_DIR / "table_internalization_stderrors.tex")


if __name__ == "__main__":
    main()
