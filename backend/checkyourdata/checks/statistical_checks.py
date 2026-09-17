import pandas as pd

from checkyourdata.baseline import population_stability_index
from checkyourdata.checks.registry import register
from checkyourdata.schema import CheckConfig, CheckType


def _relative_diff(current: float, baseline: float) -> float:
    if baseline == 0:
        return 0.0 if current == 0 else float("inf")
    return abs(current - baseline) / abs(baseline)


@register(CheckType.OUTLIER_RATE_MAX)
def outlier_rate_max(df: pd.DataFrame, check: CheckConfig) -> tuple[bool, dict]:
    column = df[check.column].dropna()
    std_devs = check.params.get("std_devs", 3)
    max_rate = check.params.get("max_rate", 0.01)

    mean = column.mean()
    std = column.std()
    if std == 0 or pd.isna(std):
        outlier_rate = 0.0
    else:
        outliers = (column - mean).abs() > std_devs * std
        outlier_rate = float(outliers.sum()) / len(column) if len(column) else 0.0

    return outlier_rate <= max_rate, {
        "outlier_rate": outlier_rate,
        "max_rate": max_rate,
        "mean": float(mean) if not pd.isna(mean) else None,
        "std": float(std) if not pd.isna(std) else None,
    }


def _stat_within_pct(df: pd.DataFrame, check: CheckConfig, stat_name: str) -> tuple[bool, dict]:
    column = df[check.column].dropna()
    current = getattr(column, stat_name)()
    baseline = check.params[f"baseline_{stat_name}"]
    pct_tolerance = check.params.get("pct", 0.1)

    diff_pct = _relative_diff(current, baseline)
    return bool(diff_pct <= pct_tolerance), {
        "current": float(current) if not pd.isna(current) else None,
        "baseline": baseline,
        "diff_pct": float(diff_pct),
        "pct_tolerance": pct_tolerance,
    }


@register(CheckType.MEAN_WITHIN_PCT)
def mean_within_pct(df: pd.DataFrame, check: CheckConfig) -> tuple[bool, dict]:
    return _stat_within_pct(df, check, "mean")


@register(CheckType.MEDIAN_WITHIN_PCT)
def median_within_pct(df: pd.DataFrame, check: CheckConfig) -> tuple[bool, dict]:
    return _stat_within_pct(df, check, "median")


@register(CheckType.STD_DEV_WITHIN_PCT)
def std_dev_within_pct(df: pd.DataFrame, check: CheckConfig) -> tuple[bool, dict]:
    return _stat_within_pct(df, check, "std")


@register(CheckType.DISTRIBUTION_SHIFT)
def distribution_shift(df: pd.DataFrame, check: CheckConfig) -> tuple[bool, dict]:
    current = df[check.column].dropna()
    baseline = pd.Series(check.params["baseline_values"])
    max_psi = check.params.get("max_psi", 0.25)

    psi = population_stability_index(baseline, current)
    return psi <= max_psi, {"psi": psi, "max_psi": max_psi}


@register(CheckType.PERCENTILE_RANGE)
def percentile_range(df: pd.DataFrame, check: CheckConfig) -> tuple[bool, dict]:
    column = df[check.column].dropna()
    percentile = check.params["percentile"]
    min_bound = check.params.get("min")
    max_bound = check.params.get("max")

    value = float(column.quantile(percentile)) if not column.empty else None
    passed = value is not None and (min_bound is None or value >= min_bound) and (max_bound is None or value <= max_bound)
    return passed, {"percentile": percentile, "value": value, "min": min_bound, "max": max_bound}
