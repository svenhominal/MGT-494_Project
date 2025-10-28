from __future__ import annotations

import io
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional, Sequence, Tuple

import numpy as np
import pandas as pd

from config import STATA_DATA_DIR, TABLES_DIR, FIGURES_DIR, ensure_output_dirs

try:
    import statsmodels.api as sm
    import statsmodels.formula.api as smf
except Exception:  # pragma: no cover
    sm = None  # type: ignore
    smf = None  # type: ignore

try:
    from linearmodels.iv import IV2SLS
except Exception:  # pragma: no cover
    IV2SLS = None  # type: ignore


def load_stata(filename: str | Path) -> pd.DataFrame:
    """
    Load a .dta file from `stata_data` or an absolute/relative path.
    """
    p = Path(filename)
    if not p.suffix:
        p = p.with_suffix(".dta")
    if not p.is_absolute():
        p = STATA_DATA_DIR / p
    return pd.read_stata(p)


def save_figure(path: str | Path) -> Path:
    p = Path(path)
    if not p.is_absolute():
        p = FIGURES_DIR / p
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def write_text(path: str | Path, text: str) -> None:
    p = Path(path)
    if not p.is_absolute():
        p = TABLES_DIR / p
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def latex_table(header: str, rows: Sequence[Sequence[str]], caption: str, label: str,
                col_align: Optional[str] = None, width: float = 0.9) -> str:
    """
    Minimal LaTeX table generator similar to Stata `file write` output.
    - header: a single row header string (already LaTeX escaped).
    - rows: list of rows, each already escaped, with cells including & and ending with \\
    - caption, label: metadata.
    - col_align: e.g. 'l c c c'. If None, infer l + ' c' * (ncols-1) based on header.
    """
    # Count columns from header by counting '&'
    ncols = header.count('&') + 1
    if col_align is None:
        col_align = 'l' + ' c' * (ncols - 1)
    buf = io.StringIO()
    buf.write("\\begin{table}\n")
    buf.write("\\centering\n")
    buf.write(f"\\caption{{{caption}}} \\label{{{label}}}\n\n")
    buf.write(f"\\begin{{tabular*}}{{.{width}\\textwidth}}{{@{{\\extracolsep{{\\fill}}}} {col_align} }}\n")
    buf.write("\\hline\\hline\n")
    buf.write(header + "\\\n")
    for r in rows:
        buf.write(" ".join(r) + "\\\n")
    buf.write("\\hline\\hline\n")
    buf.write("\\end{tabular*}\n")
    buf.write("\\end{table}\n")
    return buf.getvalue()


def add_categorical_dummies(df: pd.DataFrame, cols: Sequence[str], drop_first: bool = True,
                            prefix: Optional[str] = None) -> pd.DataFrame:
    """
    Return dummy variables for given categorical columns.
    """
    dummies = []
    for c in cols:
        d = pd.get_dummies(df[c].astype('category'), prefix=(prefix or c), drop_first=drop_first)
        dummies.append(d)
    if dummies:
        return pd.concat(dummies, axis=1)
    return pd.DataFrame(index=df.index)


def add_interaction_with_continuous(df: pd.DataFrame, cat: str, cont: str, prefix: Optional[str] = None,
                                    drop_first: bool = True) -> pd.DataFrame:
    """
    Create interactions C(cat):cont by multiplying cont with dummies for cat.
    """
    d = pd.get_dummies(df[cat].astype('category'), prefix=(prefix or f"{cat}X{cont}"), drop_first=drop_first)
    for col in d.columns:
        d[col] = d[col] * df[cont].values
    return d


@dataclass
class RegressionResult:
    model: object
    params: pd.Series
    bse: pd.Series
    nobs: int
    f_first_stage: Optional[float] = None


def fit_ols(y: pd.Series, X: pd.DataFrame, robust: bool = True,
            clusters: Optional[pd.Series] = None) -> RegressionResult:
    if sm is None:
        raise RuntimeError("statsmodels is required for OLS regressions")
    X_ = sm.add_constant(X, has_constant='add')
    model = sm.OLS(y, X_)
    if clusters is not None:
        res = model.fit(cov_type='cluster', cov_kwds={'groups': clusters})
    elif robust:
        res = model.fit(cov_type='HC1')
    else:
        res = model.fit()
    params = res.params
    bse = res.bse
    return RegressionResult(model=res, params=params, bse=bse, nobs=int(res.nobs))


def fit_iv_2sls(y: pd.Series,
                exog: pd.DataFrame,
                endog: pd.DataFrame,
                instruments: pd.DataFrame,
                robust: bool = True,
                clusters: Optional[pd.Series] = None) -> RegressionResult:
    """
    2SLS using linearmodels if available; otherwise manual two-stage with OLS.
    Returns coefficients on both exog and endog combined, with robust/clustered SE if possible.
    """
    if IV2SLS is not None:
        # Build design matrices including constant
        X = exog.copy()
        X = sm.add_constant(X, has_constant='add') if sm is not None else X
        mod = IV2SLS(y, X, endog, instruments)
        if clusters is not None:
            res = mod.fit(cov_type='clustered', clusters=clusters)
        elif robust:
            res = mod.fit(cov_type='robust')
        else:
            res = mod.fit()
        params = res.params
        bse = res.std_errors
        f_first = None
        try:
            # if single endogenous var, first_stage is a dict-like; extract F-stat
            fs = res.first_stage
            # pick the first element if dict-like
            if isinstance(fs, dict):
                fs = next(iter(fs.values()))
            f_first = float(getattr(fs, 'f_stat', np.nan)) if hasattr(fs, 'f_stat') else None
        except Exception:
            f_first = None
        return RegressionResult(model=res, params=params, bse=bse, nobs=int(res.nobs), f_first_stage=f_first)

    # Fallback: manual two-stage, robust SE
    if sm is None:
        raise RuntimeError("statsmodels is required for IV (fallback) regressions")

    # First stage: regress endog on instruments + exog
    X_first = pd.concat([exog, instruments], axis=1)
    X_first = sm.add_constant(X_first, has_constant='add')
    fitted = {}
    for col in endog.columns:
        m = sm.OLS(endog[col], X_first)
        if clusters is not None:
            r = m.fit(cov_type='cluster', cov_kwds={'groups': clusters})
        elif robust:
            r = m.fit(cov_type='HC1')
        else:
            r = m.fit()
        fitted[col] = r.fittedvalues

    endog_hat = pd.DataFrame(fitted)

    # Second stage: y on exog + fitted endog
    X_second = pd.concat([exog, endog_hat], axis=1)
    X_second = sm.add_constant(X_second, has_constant='add')
    m2 = sm.OLS(y, X_second)
    if clusters is not None:
        r2 = m2.fit(cov_type='cluster', cov_kwds={'groups': clusters})
    elif robust:
        r2 = m2.fit(cov_type='HC1')
    else:
        r2 = m2.fit()
    return RegressionResult(model=r2, params=r2.params, bse=r2.bse, nobs=int(r2.nobs), f_first_stage=None)


def sanitize_cols(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure numeric dtypes for regression columns and drop rows with any NA in those."""
    for c in df.columns:
        if df[c].dtype == 'O':
            try:
                df[c] = pd.to_numeric(df[c])
            except Exception:
                pass
    return df


def setup():
    """Call at entry to ensure dirs exist and pandas options are reasonable."""
    ensure_output_dirs()
    pd.set_option('display.width', 120)
    pd.set_option('display.max_columns', 200)

