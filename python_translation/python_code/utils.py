"""
Shared helpers for translating Stata .do workflows to Python.

The utilities here provide consistent paths, basic I/O helpers,
and wrappers around common econometric tasks (IV estimation and
LaTeX table writing) used across the translated scripts.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterable, Mapping, Optional, Sequence

import numpy as np
import pandas as pd
from linearmodels.iv import IV2SLS


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "stata_data"
TABLE_DIR = BASE_DIR / "tables"
FIG_DIR = BASE_DIR / "figures"


def ensure_output_dirs() -> None:
    """
    Create output directories (tables/ and figures/) if they do not exist.
    """
    for path in (TABLE_DIR, FIG_DIR):
        path.mkdir(parents=True, exist_ok=True)


def load_stata(filename: str) -> pd.DataFrame:
    """
    Load a Stata dataset from the standard data directory.

    Parameters
    ----------
    filename: str
        File name inside the stata_data directory.

    Returns
    -------
    pandas.DataFrame
    """
    path = DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Cannot find {path}")
    return pd.read_stata(path)


def build_iv_formula(
    dep: str,
    endog: Sequence[str],
    instruments: Sequence[str],
    exog: Sequence[str],
    include_const: bool = True,
) -> str:
    """
    Build a linearmodels IV2SLS formula matching Stata's ivreg syntax.

    Parameters
    ----------
    dep: str
        Dependent variable name.
    endog: Sequence[str]
        Endogenous regressors to be instrumented.
    instruments: Sequence[str]
        Instruments corresponding to the endogenous regressors.
    exog: Sequence[str]
        Exogenous regressors and fixed effects.
    include_const: bool, default True
        Whether to include an intercept term.

    Returns
    -------
    str
        A Patsy-style IV formula.
    """
    const_term = "1" if include_const else "-1"
    exog_part = " + ".join(exog) if exog else ""
    endog_block = " + ".join(endog)
    instr_block = " + ".join(instruments)
    if exog_part:
        left = f"{dep} ~ {const_term} + {exog_part}"
    else:
        left = f"{dep} ~ {const_term}"
    return f"{left} + [{endog_block} ~ {instr_block}]"


def run_iv(
    data: pd.DataFrame,
    dep: str,
    endog: Sequence[str],
    instruments: Sequence[str],
    exog: Sequence[str],
    cov_type: str = "robust",
    clusters: Optional[pd.Series] = None,
    include_const: bool = True,
) -> IV2SLS:
    """
    Estimate an IV regression with robust or clustered standard errors.

    Parameters
    ----------
    data: pandas.DataFrame
        Data to be used in the regression.
    dep: str
        Dependent variable name.
    endog: Sequence[str]
        Endogenous regressors.
    instruments: Sequence[str]
        Instruments for the endogenous regressors.
    exog: Sequence[str]
        Exogenous controls (including categorical terms expressed with `C()`).
    cov_type: str, default "robust"
        Covariance estimator to request from linearmodels.
    clusters: pandas.Series, optional
        Cluster identifiers when cov_type is "clustered".
    include_const: bool, default True
        Include an intercept if True, equivalent to Stata's default.

    Returns
    -------
    linearmodels.iv.results.IVResults
    """
    formula = build_iv_formula(dep, endog, instruments, exog, include_const=include_const)
    return IV2SLS.from_formula(formula, data=data).fit(
        cov_type=cov_type, debiased=True, clusters=clusters
    )


def f_stat_for_endog(result: IV2SLS, endog_var: str) -> Optional[float]:
    """
    Extract the first-stage F-statistic for a given endogenous regressor.

    Parameters
    ----------
    result: IV2SLS
        Fitted IV regression result.
    endog_var: str
        Name of the endogenous variable of interest.

    Returns
    -------
    float or None
        The F-statistic value if available.
    """
    try:
        f_stat = result.first_stage[endog_var].f_statistic
    except (KeyError, AttributeError):
        return None
    if f_stat is None:
        return None
    return float(np.asarray(f_stat.stat))


def write_text(path: Path, content: str) -> None:
    """
    Write plain text (e.g., logs or LaTeX tables) to disk.

    Parameters
    ----------
    path: pathlib.Path
        Destination path.
    content: str
        Text content to save.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def fmt(val: Optional[float], precision: int = 3) -> str:
    """
    Format a numeric value with a fixed number of decimals.

    Parameters
    ----------
    val: float or None
        Value to format.
    precision: int, default 3
        Number of decimals.

    Returns
    -------
    str
        Formatted string or empty string if val is None.
    """
    if val is None:
        return ""
    return f"{val:.{precision}f}"


def setup_logging(log_path: Optional[Path]) -> None:
    """
    Configure a simple file logger mirroring Stata's `log using`.

    Parameters
    ----------
    log_path: pathlib.Path or None
        Log file to write. If None, logging is not configured.
    """
    if log_path is None:
        return
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        handlers=[logging.FileHandler(log_path, mode="w", encoding="utf-8")],
    )

