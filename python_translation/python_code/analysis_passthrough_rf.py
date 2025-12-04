"""
Translation of `analysis_passthrough_rf.do` to Python.

The script runs the pass-through regressions, constructs LaTeX tables,
and mirrors the output file names used in the Stata code.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from linearmodels.iv import IV2SLS

from utils import (
    TABLE_DIR,
    ensure_output_dirs,
    fmt,
    load_stata,
    run_iv,
    write_text,
)


np.random.seed(42)

SUPPLY_CONTROLS = ["windx", "windx2"]
DEMAND_CONTROLS = ["temp", "tempx", "humid"]
BASE_CONTROLS = ["coal", "gas", "brent"]
BASE_FE = ["C(hour)", "C(year)", "C(weekd)", "C(month)"]
MONTH_YEAR_FE = ["C(month):C(year)"]
MONTH_TEMP_FE = ["C(month):temp", "C(month):tempx"]
MONTH_HOUR_FE = ["C(month):C(hour)"]
HOUR_INPUT_INTERACTIONS = ["C(hour):coal", "C(hour):gas", "C(hour):brent"]


@dataclass
class SpecOutcome:
    """
    Container for an IV specification and its first-stage diagnostics.
    """

    name: str
    iv: IV2SLS
    first_stage: Optional[smf.ols] = None
    f_stat: Optional[float] = None


def _raw_vars_from_terms(terms: Iterable[str]) -> List[str]:
    """
    Extract underlying variable names from Patsy-style terms.
    """
    vars_found: List[str] = []
    for term in terms:
        cleaned = term.replace("C(", "").replace(")", "")
        for part in cleaned.replace(" ", "").split(":"):
            if part and part not in vars_found:
                vars_found.append(part)
    return vars_found


def _prep_data(
    df: pd.DataFrame,
    dep: str,
    endog: Sequence[str],
    instruments: Sequence[str],
    exog_terms: Sequence[str],
    drop_condition: Optional[pd.Series] = None,
) -> pd.DataFrame:
    """
    Apply sample restrictions and drop missing observations for a given model.
    """
    needed_vars = set([dep, *endog, *instruments] + _raw_vars_from_terms(exog_terms))
    subset = df.copy()
    if drop_condition is not None:
        subset = subset.loc[drop_condition].copy()
    subset = subset.dropna(subset=list(needed_vars))
    return subset


def _run_first_stage(
    df: pd.DataFrame, dep: str, instruments: Sequence[str], exog_terms: Sequence[str]
) -> Tuple[Optional[smf.ols], Optional[float]]:
    """
    Run the first-stage OLS regression mirroring Stata's `regress` call.
    """
    if not instruments:
        return None, None
    rhs = instruments + list(exog_terms)
    formula = f"{dep} ~ 1 + " + " + ".join(rhs)
    model = smf.ols(formula, data=df).fit(cov_type="HC1")
    hyp_parts = []
    for param in model.params.index:
        if any(inst in param for inst in instruments):
            if any(char in param for char in ("[", "]", ":", ".")):
                hyp_parts.append(f"Q('{param}') = 0")
            else:
                hyp_parts.append(f"{param} = 0")
    f_stat = None
    if hyp_parts:
        hypothesis = ", ".join(hyp_parts)
        f_stat = float(model.f_test(hypothesis).fvalue)
    return model, f_stat


def _collect_coef(result: IV2SLS, var: str) -> Tuple[Optional[float], Optional[float]]:
    """
    Safely extract coefficient and robust standard error for a variable.
    """
    try:
        beta = float(result.params[var])
        se = float(result.std_errors[var])
        return beta, se
    except KeyError:
        return None, None


def _latex_row(values: Sequence[str]) -> str:
    """
    Join items into a LaTeX table row.
    """
    return " & ".join(values) + " \\\\"


def _log_results(outcomes: Dict[str, SpecOutcome], log_path: Path) -> None:
    """
    Save model summaries to a log file similar to Stata's log output.
    """
    logs = []
    for name, outcome in outcomes.items():
        logs.append(f"== {name} ==")
        logs.append(str(outcome.iv.summary))
        if outcome.first_stage is not None:
            logs.append(f"-- First stage ({name}) --")
            logs.append(str(outcome.first_stage.summary()))
    write_text(log_path, "\n\n".join(logs))


def _baseline_exog(use_controls1: bool, include_mon_temp: bool, include_mon_hour: bool) -> List[str]:
    """
    Assemble exogenous regressors for the baseline block.
    """
    controls = HOUR_INPUT_INTERACTIONS + BASE_CONTROLS if use_controls1 else BASE_CONTROLS
    exog = SUPPLY_CONTROLS + DEMAND_CONTROLS + controls + BASE_FE + MONTH_YEAR_FE
    if include_mon_temp:
        exog += MONTH_TEMP_FE
    if include_mon_hour:
        exog += MONTH_HOUR_FE
    return exog


def run_baseline_block(df: pd.DataFrame) -> Dict[str, SpecOutcome]:
    """
    Reproduce the baseline pass-through regressions.
    """
    df = df.dropna()
    outcomes: Dict[str, SpecOutcome] = {}
    configs = [
        ("spec1", False, False, False),
        ("spec2", True, False, False),
        ("spec3", False, True, False),
        ("spec4", True, True, False),
        ("spec5", True, True, True),
    ]
    maincost = "ecost2"
    instruments = ["eprice"]
    drop_condition = df["rd"] != 1
    for name, include_mon_temp, include_mon_hour, use_controls1 in configs:
        exog = _baseline_exog(use_controls1, include_mon_temp, include_mon_hour)
        print(exog)
        data_model = _prep_data(df, "mg_price", [maincost], instruments, exog, drop_condition)
        # print(data_model)
        iv_res = run_iv(
            data=data_model,
            dep="mg_price",
            endog=[maincost],
            instruments=instruments,
            exog=exog,
            cov_type="robust",
        )
        fs_res, f_stat = _run_first_stage(data_model, maincost, instruments, exog)
        outcomes[name] = SpecOutcome(name=name, iv=iv_res, first_stage=fs_res, f_stat=f_stat)
    return outcomes


def run_additional_block(df: pd.DataFrame) -> Dict[str, SpecOutcome]:
    """
    Additional pass-through specifications with quadratic terms and trends.
    """
    outcomes: Dict[str, SpecOutcome] = {}
    configs = [
        ("spec_add1", []),
        ("spec_add2", ["coal2", "gas2", "brent2"]),
        ("spec_add3", ["coal2", "gas2", "brent2", "temp2"]),
        ("spec_add4", ["coal2", "gas2", "brent2", "temp2", "windtime"]),
    ]
    maincost = "ecost2"
    instruments = ["eprice"]
    base_exog = (
        SUPPLY_CONTROLS
        + DEMAND_CONTROLS
        + HOUR_INPUT_INTERACTIONS
        + BASE_CONTROLS
        + BASE_FE
        + MONTH_YEAR_FE
        + MONTH_HOUR_FE
        + MONTH_TEMP_FE
    )
    drop_condition = df["rd"] != 1
    for name, extra in configs:
        exog = base_exog + extra
        data_model = _prep_data(df, "mg_price", [maincost], instruments, exog, drop_condition)
        iv_res = run_iv(
            data=data_model,
            dep="mg_price",
            endog=[maincost],
            instruments=instruments,
            exog=exog,
            cov_type="robust",
        )
        fs_res, f_stat = _run_first_stage(data_model, maincost, instruments, exog)
        outcomes[name] = SpecOutcome(name=name, iv=iv_res, first_stage=fs_res, f_stat=f_stat)
    return outcomes


def run_interpolated_block(df: pd.DataFrame) -> Tuple[Dict[str, SpecOutcome], Dict[str, SpecOutcome]]:
    """
    Specifications using interpolated emissions costs and exact assignment.
    """
    specs: Dict[str, SpecOutcome] = {}
    specs_exact: Dict[str, SpecOutcome] = {}
    instruments = ["eprice"]
    drop_condition = df["rd"] != 1
    configs = [
        ("spec1", False, False),
        ("spec2", True, False),
        ("spec3", False, True),
        ("spec4", True, True),
        ("spec5", True, True, True),
    ]
    for name, include_mon_temp, include_mon_hour, *rest in configs:
        use_controls1 = bool(rest[0]) if rest else False
        exog = _baseline_exog(use_controls1, include_mon_temp, include_mon_hour)
        for maincost, target in [("ecost_int", specs), ("ecost", specs_exact)]:
            data_model = _prep_data(df, "mg_price", [maincost], instruments, exog, drop_condition)
            iv_res = run_iv(
                data=data_model,
                dep="mg_price",
                endog=[maincost],
                instruments=instruments,
                exog=exog,
                cov_type="robust",
            )
            fs_res, f_stat = _run_first_stage(data_model, maincost, instruments, exog)
            target[name] = SpecOutcome(name=name, iv=iv_res, first_stage=fs_res, f_stat=f_stat)
    return specs, specs_exact


def run_rd_block(df: pd.DataFrame) -> Dict[str, SpecOutcome]:
    """
    Regressions including the Royal Decree period.
    """
    outcomes: Dict[str, SpecOutcome] = {}
    configs = [
        ("spec1", False, False, False),
        ("spec2", True, False, False),
        ("spec3", False, True, False),
        ("spec4", True, True, False),
        ("spec5", True, True, True),
    ]
    maincost = "ecost2"
    instruments = ["eprice"]
    for name, include_mon_temp, include_mon_hour, use_controls1 in configs:
        exog = _baseline_exog(use_controls1, include_mon_temp, include_mon_hour)
        data_model = _prep_data(df, "mg_price", [maincost], instruments, exog, None)
        iv_res = run_iv(
            data=data_model,
            dep="mg_price",
            endog=[maincost],
            instruments=instruments,
            exog=exog,
            cov_type="robust",
        )
        fs_res, f_stat = _run_first_stage(data_model, maincost, instruments, exog)
        outcomes[name] = SpecOutcome(name=name, iv=iv_res, first_stage=fs_res, f_stat=f_stat)
    return outcomes


def run_peak_block(df: pd.DataFrame) -> Dict[str, SpecOutcome]:
    """
    Peak vs. off-peak regressions.
    """
    outcomes: Dict[str, SpecOutcome] = {}
    configs = [
        ("spec1", False, False, False),
        ("spec2", True, False, False),
        ("spec3", False, True, False),
        ("spec4", True, True, False),
        ("spec5", True, True, True),
    ]
    maincosts = ["ecost2_peak", "ecost2_off"]
    instruments = ["eprice", "C(peak):eprice"]
    drop_condition = df["rd"] != 1
    for name, include_mon_temp, include_mon_hour, use_controls1 in configs:
        exog = _baseline_exog(use_controls1, include_mon_temp, include_mon_hour)
        data_model = _prep_data(df, "mg_price", maincosts, instruments, exog, drop_condition)
        iv_res = run_iv(
            data=data_model,
            dep="mg_price",
            endog=maincosts,
            instruments=instruments,
            exog=exog,
            cov_type="robust",
        )
        outcomes[name] = SpecOutcome(name=name, iv=iv_res, first_stage=None, f_stat=None)
    return outcomes


def run_peak_alternatives(df: pd.DataFrame) -> Dict[str, SpecOutcome]:
    """
    Alternative peak/off-peak regressions comparing emissions and total costs.
    """
    outcomes: Dict[str, SpecOutcome] = {}
    base_exog = [
        "C(year)",
        "C(month)",
        "C(year):C(month)",
        "C(weekd)",
        "C(month):C(hour)",
    ]
    exog_linear = SUPPLY_CONTROLS + DEMAND_CONTROLS + HOUR_INPUT_INTERACTIONS + BASE_CONTROLS + base_exog
    exog_logs = [
        term.replace("coal", "lcoal").replace("gas", "lgas").replace("brent", "lbrent")
        for term in exog_linear
    ]

    data_subset = df.loc[(df["rd"] != 1) & df["totalcost2"].notna()].copy()
    outcomes["spec_peaka1"] = SpecOutcome(
        name="spec_peaka1",
        iv=run_iv(
            data=data_subset,
            dep="mg_price",
            endog=["ecost2_peak", "ecost2_off"],
            instruments=["eprice", "C(peak):eprice"],
            exog=exog_linear,
            cov_type="robust",
        ),
    )
    outcomes["spec_peaka2"] = SpecOutcome(
        name="spec_peaka2",
        iv=run_iv(
            data=data_subset,
            dep="lmg_price",
            endog=["lecost2_peak", "lecost2_off"],
            instruments=["leprice", "C(peak):leprice"],
            exog=exog_logs,
            cov_type="robust",
        ),
    )
    outcomes["spec_peaka3"] = SpecOutcome(
        name="spec_peaka3",
        iv=run_iv(
            data=data_subset,
            dep="mg_price",
            endog=["totalcost2_peak", "totalcost2_off"],
            instruments=["eprice", "C(peak):eprice"],
            exog=exog_linear,
            cov_type="robust",
        ),
    )
    outcomes["spec_peaka4"] = SpecOutcome(
        name="spec_peaka4",
        iv=run_iv(
            data=data_subset,
            dep="lmg_price",
            endog=["ltotalcost2_peak", "ltotalcost2_off"],
            instruments=["leprice", "C(peak):leprice"],
            exog=exog_logs,
            cov_type="robust",
        ),
    )
    return outcomes


def run_trend_block(df: pd.DataFrame, include_rd: bool) -> Dict[str, SpecOutcome]:
    """
    Robustness regressions with linear time trends.
    """
    outcomes: Dict[str, SpecOutcome] = {}
    configs = [
        ("spec1", ["C(ym)"]),
        ("spec2", ["C(ym)", "C(ym):time"]),
        ("spec3", ["C(ym)", "C(yb):time"]),
        ("spec4", ["C(ym)", "C(yq):time"]),
    ]
    maincosts = ["ecost2_peak", "ecost2_off"]
    instruments = ["eprice", "C(peak):eprice"]
    exog_base = (
        SUPPLY_CONTROLS
        + DEMAND_CONTROLS
        + HOUR_INPUT_INTERACTIONS
        + BASE_CONTROLS
        + BASE_FE
        + MONTH_HOUR_FE
        + MONTH_TEMP_FE
    )
    for name, trend_terms in configs:
        exog = exog_base + trend_terms
        data_model = _prep_data(
            df,
            "mg_price",
            maincosts,
            instruments,
            exog,
            None if include_rd else (df["rd"] == 0),
        )
        iv_res = run_iv(
            data=data_model,
            dep="mg_price",
            endog=maincosts,
            instruments=instruments,
            exog=exog,
            cov_type="robust",
        )
        outcomes[name + ("_rd" if include_rd else "")] = SpecOutcome(
            name=name + ("_rd" if include_rd else ""), iv=iv_res
        )
    return outcomes


def _baseline_table(outcomes: Dict[str, SpecOutcome], table_path: Path, note: str) -> None:
    """
    Write LaTeX tables for the baseline IV regressions.
    """
    rows = []
    header = ["", "\\textbf{(1)}", "\\textbf{(2)}", "\\textbf{(3)}", "\\textbf{(4)}", "\\textbf{(5)}"]
    rows.append(_latex_row(header))
    coef_row = ["Mg. Emissions Costs $(\\rho)$"]
    se_row = [""]
    for key in ["spec1", "spec2", "spec3", "spec4", "spec5"]:
        beta, se = _collect_coef(outcomes[key].iv, "ecost2")
        coef_row.append(fmt(beta))
        se_row.append(f"({fmt(se)})")
    rows.append(_latex_row(coef_row))
    rows.append(_latex_row(se_row))
    rows.append("\\hline")
    temp_row = ["Temperature"]
    temp_se_row = [""]
    tempx_row = ["Maximum Temperature"]
    tempx_se_row = [""]
    for key in ["spec1", "spec2", "spec3", "spec4", "spec5"]:
        beta, se = _collect_coef(outcomes[key].iv, "temp")
        temp_row.append(fmt(beta) if beta is not None and key in ("spec1", "spec3") else "")
        temp_se_row.append(f"({fmt(se)})" if se is not None and key in ("spec1", "spec3") else "")
        beta_x, se_x = _collect_coef(outcomes[key].iv, "tempx")
        tempx_row.append(fmt(beta_x) if beta_x is not None and key in ("spec1", "spec3") else "")
        tempx_se_row.append(f"({fmt(se_x)})" if se_x is not None and key in ("spec1", "spec3") else "")
    rows.extend([_latex_row(temp_row), _latex_row(temp_se_row), _latex_row(tempx_row), _latex_row(tempx_se_row)])
    for var, label, specs in [
        ("windx", "Wind Speed", ["spec1", "spec2", "spec3", "spec4", "spec5"]),
        ("windx2", "Wind Speed Squared", ["spec1", "spec2", "spec3", "spec4", "spec5"]),
        ("coal", "Coal", ["spec1", "spec2", "spec3", "spec4"]),
        ("gas", "Gas", ["spec1", "spec2", "spec3", "spec4"]),
        ("brent", "Brent", ["spec1", "spec2", "spec3", "spec4"]),
    ]:
        coef_row = [label]
        se_row = [""]
        for key in ["spec1", "spec2", "spec3", "spec4", "spec5"]:
            beta, se = _collect_coef(outcomes[key].iv, var)
            coef_row.append(fmt(beta) if key in specs and beta is not None else "")
            se_row.append(f"({fmt(se)})" if key in specs and se is not None else "")
        rows.append(_latex_row(coef_row))
        rows.append(_latex_row(se_row))
    f_row = ["F-test"]
    for key in ["spec1", "spec2", "spec3", "spec4", "spec5"]:
        f_row.append(fmt(outcomes[key].f_stat, 1) if outcomes[key].f_stat is not None else "")
    rows.append(_latex_row(f_row))
    content = [
        "\\begin{table}",
        "\\centering",
        "\\caption{Cost Pass-through Regression Results} \\label{tab:cost_pt}",
        "\\begin{tabular*}{.9\\textwidth}{@{\\extracolsep{\\fill}} l c c c c c}",
        "\\hline\\hline",
    ]
    content += rows
    content += [
        "\\hline\\hline",
        "\\end{tabular*}",
        "\\begin{minipage}[c]{.9\\textwidth}",
        "{\\footnotesize",
        note,
        "}",
        "\\end{minipage}",
        "\\end{table}",
    ]
    write_text(table_path, "\n".join(content))


def _first_stage_table(outcomes: Dict[str, SpecOutcome], table_path: Path, note: str) -> None:
    """
    Write the first-stage LaTeX table.
    """
    rows = []
    header = ["", "\\textbf{(1)}", "\\textbf{(2)}", "\\textbf{(3)}", "\\textbf{(4)}", "\\textbf{(5)}"]
    rows.append(_latex_row(header))
    coef_row = ["Emissions Price"]
    se_row = [""]
    temp_row = ["Temperature"]
    tempx_row = ["Maximum Temperature"]
    temp_se_row = [""]
    tempx_se_row = [""]
    for key in ["spec1", "spec2", "spec3", "spec4", "spec5"]:
        fs = outcomes[key].first_stage
        if fs is not None:
            coef_row.append(fmt(fs.params.get("eprice")))
            se_row.append(f"({fmt(fs.bse.get('eprice'))})")
            temp_row.append(fmt(fs.params.get("temp")) if key in ("spec1", "spec3") else "")
            temp_se_row.append(f"({fmt(fs.bse.get('temp'))})" if key in ("spec1", "spec3") else "")
            tempx_row.append(fmt(fs.params.get("tempx")) if key in ("spec1", "spec3") else "")
            tempx_se_row.append(f"({fmt(fs.bse.get('tempx'))})" if key in ("spec1", "spec3") else "")
        else:
            coef_row.append("")
            se_row.append("")
            temp_row.append("")
            temp_se_row.append("")
            tempx_row.append("")
            tempx_se_row.append("")
    rows.extend(
        [
            _latex_row(coef_row),
            _latex_row(se_row),
            _latex_row(temp_row),
            _latex_row(temp_se_row),
            _latex_row(tempx_row),
            _latex_row(tempx_se_row),
        ]
    )
    for var, label, specs in [
        ("windx", "Wind Speed", ["spec1", "spec2", "spec3", "spec4", "spec5"]),
        ("windx2", "Wind Speed Squared", ["spec1", "spec2", "spec3", "spec4", "spec5"]),
        ("coal", "Coal", ["spec1", "spec2", "spec3", "spec4"]),
        ("gas", "Gas", ["spec1", "spec2", "spec3", "spec4"]),
        ("brent", "Brent", ["spec1", "spec2", "spec3", "spec4"]),
    ]:
        coef_row = [label]
        se_row = [""]
        for key in ["spec1", "spec2", "spec3", "spec4", "spec5"]:
            fs = outcomes[key].first_stage
            if fs is not None and key in specs:
                coef_row.append(fmt(fs.params.get(var)))
                se_row.append(f"({fmt(fs.bse.get(var))})")
            else:
                coef_row.append("")
                se_row.append("")
        rows.append(_latex_row(coef_row))
        rows.append(_latex_row(se_row))
    content = [
        "\\begin{table}[!ht]",
        "\\centering",
        "\\caption{First Stage for Marginal Emissions Costs} \\label{tab:cost_pt_first}",
        "\\begin{tabular*}{.9\\textwidth}{@{\\extracolsep{\\fill}} l c c c c c}",
        "\\hline\\hline",
    ]
    content += rows
    content += [
        "\\hline\\hline",
        "\\end{tabular*}",
        "\\begin{minipage}[c]{.9\\textwidth}",
        "{\\footnotesize",
        note,
        "}",
        "\\end{minipage}",
        "\\end{table}",
    ]
    write_text(table_path, "\n".join(content))


def _generic_table(
    outcomes: Dict[str, SpecOutcome],
    var_label_pairs: List[Tuple[str, str]],
    table_path: Path,
    caption: str,
    label: str,
    notes: str,
) -> None:
    """
    Write a compact LaTeX table for robustness blocks.
    """
    header_keys = list(outcomes.keys())
    header = [""] + [f"\\textbf{{({i+1})}}" for i in range(len(header_keys))]
    rows = [_latex_row(header)]
    for var, label_text in var_label_pairs:
        coef_row = [label_text]
        se_row = [""]
        for key in header_keys:
            beta, se = _collect_coef(outcomes[key].iv, var)
            coef_row.append(fmt(beta))
            se_row.append(f"({fmt(se)})")
        rows.append(_latex_row(coef_row))
        rows.append(_latex_row(se_row))
    content = [
        "\\begin{table}",
        "\\centering",
        f"\\caption{{{caption}}} \\label{{{label}}}",
        r"\\begin{tabular*}"+f"{{.9\\textwidth}}{{@{{\\extracolsep{{\\fill}}}} l {' '.join(['c' for _ in header_keys])}}}",
        "\\hline\\hline",
    ]
    content += rows
    content += [
        "\\hline\\hline",
        "\\end{tabular*}",
        "\\begin{minipage}[c]{.9\\textwidth}",
        "{\\footnotesize",
        notes,
        "}",
        "\\end{minipage}",
        "\\end{table}",
    ]
    write_text(table_path, "\n".join(content))


def _peak_alternative_table(outcomes: Dict[str, SpecOutcome], table_path: Path, notes: str) -> None:
    """
    Table comparing emissions vs. total costs (peak vs off-peak).
    """
    header = ["", "\\textbf{Emissions Costs}", "", "\\textbf{Total Mg. Costs}", ""]
    sub_header = ["", "Linear", "Logs", "Linear", "Logs"]
    rows = [_latex_row(header), _latex_row(sub_header)]
    for label_text, var_list in [
        ("Peak Pass-Through", ["ecost2_peak", "lecost2_peak", "totalcost2_peak", "ltotalcost2_peak"]),
        ("Off-Peak Pass-Through", ["ecost2_off", "lecost2_off", "totalcost2_off", "ltotalcost2_off"]),
    ]:
        coef_row = [label_text]
        se_row = [""]
        for var in var_list:
            spec_key = {
                "ecost2_peak": "spec_peaka1",
                "ecost2_off": "spec_peaka1",
                "lecost2_peak": "spec_peaka2",
                "lecost2_off": "spec_peaka2",
                "totalcost2_peak": "spec_peaka3",
                "totalcost2_off": "spec_peaka3",
                "ltotalcost2_peak": "spec_peaka4",
                "ltotalcost2_off": "spec_peaka4",
            }[var]
            beta, se = _collect_coef(outcomes[spec_key].iv, var)
            coef_row.append(fmt(beta))
            se_row.append(f"({fmt(se)})")
        rows.append(_latex_row(coef_row))
        rows.append(_latex_row(se_row))
    content = [
        "\\begin{table}",
        "\\centering",
        "\\caption{Emissions vs. Non Emissions Costs: Peak vs. Off-Peak} \\label{tab:cost_pt_peak_alternatives}",
        "\\begin{tabular*}{.9\\textwidth}{@{\\extracolsep{\\fill}} l c c c c}",
        "\\hline\\hline",
    ]
    content += rows
    content += [
        "\\hline\\hline",
        "\\end{tabular*}",
        "\\begin{minipage}[c]{.9\\textwidth}",
        "{\\footnotesize",
        notes,
        "}",
        "\\end{minipage}",
        "\\end{table}",
    ]
    write_text(table_path, "\n".join(content))


def main() -> None:
    """
    Run all pass-through regressions and write LaTeX tables/logs.
    """
    ensure_output_dirs()
    df = load_stata("data_regressions_passthrough.dta")

    baseline_outcomes = run_baseline_block(df)
    _log_results(baseline_outcomes, TABLE_DIR / "table_cost_pt_base.log")
    note_base = (
        "Notes: Sample from January 2004 to February 2006, includes all thermal units in the Spanish electricity "
        "market. All specifications include month of sample, weekday, and hour fixed effects, as well as weather and "
        "demand controls (temperature, maximum temperature, humidity), supply controls (wind speed and wind speed "
        "squared); and common controls (commodity prices of coal, gas, and oil). The marginal emissions cost is "
        "instrumented with the emissions price. Robust standard errors in parentheses. "
        f"Number of observations: {int(baseline_outcomes['spec1'].iv.nobs):,.0f}."
    )
    _baseline_table(baseline_outcomes, TABLE_DIR / "table_cost_pt_base.tex", note_base)
    _first_stage_table(baseline_outcomes, TABLE_DIR / "table_cost_pt_first.tex", note_base)

    additional_outcomes = run_additional_block(df)
    add_note = (
        "Notes: Sample from January 2004 to February 2006, includes all thermal units in the Spanish electricity "
        "market. All specifications include month of sample, weekday, and hour fixed effects, as well as weather and "
        "demand controls (temperature, maximum temperature, humidity), supply controls (wind speed and wind speed "
        "squared); and common controls (commodity prices of coal, gas, and oil). The marginal emissions cost is "
        "instrumented with the emissions price. Robust standard errors in parentheses. "
        f"Number of observations: {int(additional_outcomes['spec_add1'].iv.nobs):,.0f}."
    )
    _generic_table(
        additional_outcomes,
        [
            ("ecost2", "Mg. Emissions Costs $(\\rho)$"),
            ("windx", "Wind Speed"),
            ("windx2", "Wind Speed Squared"),
            ("windtime", "Wind Speed X Trend"),
        ],
        TABLE_DIR / "table_cost_pt_additional.tex",
        "Cost Pass-through Regression - Additional controls",
        "tab:cost_pt_additional",
        add_note,
    )

    interpolated_outcomes, exact_outcomes = run_interpolated_block(df)
    int_note = (
        "Notes: Sample from January 2004 to February 2006, includes all thermal units in the Spanish electricity "
        "market. All specifications include month of sample, weekday, and hour fixed effects, as well as weather and "
        "demand controls (temperature, maximum temperature, humidity), supply controls (wind speed and wind speed "
        "squared); and common controls (commodity prices of coal, gas, and oil). The marginal emissions cost is "
        "instrumented with the emissions price. Robust standard errors in parentheses."
    )
    header = ["", "\\textbf{(1)}", "\\textbf{(2)}", "\\textbf{(3)}", "\\textbf{(4)}", "\\textbf{(5)}"]
    rows = [_latex_row(header)]
    for var, label in [
        ("ecost_int", "Interpolated Emissions Costs"),
        ("ecost2", "Mg. Emissions Costs (Units & Technologies)"),
        ("ecost", "Mg. Emissions Costs (Units Only)"),
    ]:
        coef_row = [label]
        se_row = [""]
        target = interpolated_outcomes if var == "ecost_int" else (baseline_outcomes if var == "ecost2" else exact_outcomes)
        for key in ["spec1", "spec2", "spec3", "spec4", "spec5"]:
            beta, se = _collect_coef(target[key].iv, var)
            coef_row.append(fmt(beta))
            se_row.append(f"({fmt(se)})")
        rows.append(_latex_row(coef_row))
        rows.append(_latex_row(se_row))
    content = [
        "\\begin{table}",
        "\\centering",
        "\\caption{Cost Pass-through Regression Results for different Emissions Assumptions} \\label{tab:cost_pt_interpolated}",
        "\\begin{tabular*}{.9\\textwidth}{@{\\extracolsep{\\fill}} l c c c c c}",
        "\\hline\\hline",
    ] + rows + [
        "\\hline\\hline",
        "\\end{tabular*}",
        "\\begin{minipage}[c]{.9\\textwidth}",
        "{\\footnotesize",
        int_note,
        "}",
        "\\end{minipage}",
        "\\end{table}",
    ]
    write_text(TABLE_DIR / "table_cost_pt_interpolated.tex", "\n".join(content))

    rd_outcomes = run_rd_block(df)
    note_rd = (
        "Notes: Sample from January 2004 to June 2007, includes all thermal units in the Spanish electricity market. "
        "All specifications include month of sample, weekday, and hour fixed effects, as well as weather and demand "
        "controls (temperature, maximum temperature, humidity), supply controls (wind speed and wind speed squared); "
        "and common controls (commodity prices of coal, gas, and oil). The marginal emissions cost is instrumented "
        "with the emissions price. Robust standard errors in parentheses. "
        f"Number of observations: {int(rd_outcomes['spec1'].iv.nobs):,.0f}."
    )
    _baseline_table(rd_outcomes, TABLE_DIR / "table_cost_pt_rd.tex", note_rd)

    peak_outcomes = run_peak_block(df)
    note_peak = (
        "Notes: Sample from January 2004 to February 2006, includes all thermal units in the Spanish electricity "
        "market. Only peak hours are included (between 8am and 8pm). All specifications include month of sample, "
        "weekday, and hour fixed effects, as well as weather and demand controls (temperature, maximum temperature, "
        "humidity), supply controls (wind speed and wind speed squared); and common controls (commodity prices of "
        "coal, gas, and oil). The marginal emissions cost is instrumented with the emissions price. Robust standard "
        "errors in parentheses. "
        f"Number of observations: {int(peak_outcomes['spec1'].iv.nobs):,.0f}."
    )
    _generic_table(
        peak_outcomes,
        [("ecost2_peak", "Mg. Emissions Costs - Peak"), ("ecost2_off", "Mg. Emissions Costs - Off Peak")],
        TABLE_DIR / "table_cost_pt_peak.tex",
        "Cost Pass-through Regression Results: Peak vs. Non-Peak",
        "tab:cost_pt_peak",
        note_peak,
    )

    peak_alt_outcomes = run_peak_alternatives(df)
    note_peak_alt = (
        "Notes: Sample from January 2004 to February 2006, includes all thermal units in the Spanish electricity "
        "market. Only peak hours are included (between 8am and 8pm). All specifications include month of sample, "
        "weekday, and month-hour fixed effects, as well as weather and demand controls (temperature, maximum "
        "temperature, humidity), supply controls (wind speed and wind speed squared); and hourly linear "
        "(logarithmic) controls for commodity prices of coal, gas, and oil). (Log of) Costs are instrumented with "
        "(the log of) the emissions price. Robust standard errors in parentheses. "
        f"Number of observations: {int(peak_alt_outcomes['spec_peaka1'].iv.nobs):,.0f}."
    )
    _peak_alternative_table(peak_alt_outcomes, TABLE_DIR / "table_cost_pt_peak_alternatives.tex", note_peak_alt)

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
