import re

import pandas as pd

from checkyourdata.checks.registry import register
from checkyourdata.schema import CheckConfig, CheckType


@register(CheckType.NOT_NULL)
def not_null(df: pd.DataFrame, check: CheckConfig) -> tuple[bool, dict]:
    column = df[check.column]
    null_count = int(column.isna().sum())
    return null_count == 0, {"null_count": null_count, "row_count": len(column)}


@register(CheckType.NULL_PERCENTAGE_MAX)
def null_percentage_max(df: pd.DataFrame, check: CheckConfig) -> tuple[bool, dict]:
    column = df[check.column]
    max_pct = check.params["max_pct"]
    null_pct = float(column.isna().sum()) / len(column) if len(column) else 0.0
    return null_pct <= max_pct, {"null_pct": null_pct, "max_pct": max_pct}


@register(CheckType.MIN_MAX_RANGE)
def min_max_range(df: pd.DataFrame, check: CheckConfig) -> tuple[bool, dict]:
    column = df[check.column].dropna()
    min_bound = check.params.get("min")
    max_bound = check.params.get("max")

    violations = pd.Series(False, index=column.index)
    if min_bound is not None:
        violations |= column < min_bound
    if max_bound is not None:
        violations |= column > max_bound

    violation_count = int(violations.sum())
    return violation_count == 0, {
        "violation_count": violation_count,
        "observed_min": float(column.min()) if not column.empty else None,
        "observed_max": float(column.max()) if not column.empty else None,
    }


@register(CheckType.UNIQUE)
def unique(df: pd.DataFrame, check: CheckConfig) -> tuple[bool, dict]:
    column = df[check.column].dropna()
    duplicate_count = int(column.duplicated().sum())
    return duplicate_count == 0, {"duplicate_count": duplicate_count}


@register(CheckType.UNIQUENESS_PERCENTAGE_MIN)
def uniqueness_percentage_min(df: pd.DataFrame, check: CheckConfig) -> tuple[bool, dict]:
    column = df[check.column].dropna()
    min_pct = check.params["min_pct"]
    uniqueness_pct = column.nunique() / len(column) if len(column) else 1.0
    return uniqueness_pct >= min_pct, {"uniqueness_pct": uniqueness_pct, "min_pct": min_pct}


@register(CheckType.ALLOWED_VALUES)
def allowed_values(df: pd.DataFrame, check: CheckConfig) -> tuple[bool, dict]:
    column = df[check.column].dropna()
    allowed = set(check.params["values"])

    invalid_mask = ~column.isin(allowed)
    invalid_count = int(invalid_mask.sum())
    return invalid_count == 0, {
        "invalid_count": invalid_count,
        "invalid_examples": column[invalid_mask].unique().tolist()[:10],
    }


@register(CheckType.REGEX_MATCH)
def regex_match(df: pd.DataFrame, check: CheckConfig) -> tuple[bool, dict]:
    column = df[check.column].dropna().astype(str)
    pattern = re.compile(check.params["pattern"])

    non_matching = ~column.str.match(pattern)
    non_matching_count = int(non_matching.sum())
    return non_matching_count == 0, {
        "non_matching_count": non_matching_count,
        "examples": column[non_matching].unique().tolist()[:10],
    }


@register(CheckType.DATA_TYPE_CHECK)
def data_type_check(df: pd.DataFrame, check: CheckConfig) -> tuple[bool, dict]:
    column = df[check.column].dropna()
    expected_type = check.params["expected_type"]

    if expected_type in ("int", "float", "numeric"):
        coerced = pd.to_numeric(column, errors="coerce")
    elif expected_type == "datetime":
        coerced = pd.to_datetime(column, errors="coerce")
    elif expected_type == "bool":
        coerced = column.where(column.isin([True, False]))
    else:  # "string"
        coerced = column.where(column.apply(lambda v: isinstance(v, str)))

    failure_mask = coerced.isna()
    failure_count = int(failure_mask.sum())
    return failure_count == 0, {
        "failure_count": failure_count,
        "expected_type": expected_type,
        "examples": column[failure_mask].unique().tolist()[:10],
    }


@register(CheckType.STRING_LENGTH_RANGE)
def string_length_range(df: pd.DataFrame, check: CheckConfig) -> tuple[bool, dict]:
    column = df[check.column].dropna().astype(str)
    lengths = column.str.len()
    min_length = check.params.get("min_length")
    max_length = check.params.get("max_length")

    violations = pd.Series(False, index=column.index)
    if min_length is not None:
        violations |= lengths < min_length
    if max_length is not None:
        violations |= lengths > max_length

    violation_count = int(violations.sum())
    return violation_count == 0, {"violation_count": violation_count}


@register(CheckType.DATE_RANGE)
def date_range(df: pd.DataFrame, check: CheckConfig) -> tuple[bool, dict]:
    column = pd.to_datetime(df[check.column].dropna(), errors="coerce")
    not_future = check.params.get("not_future", False)
    min_date = pd.to_datetime(check.params["min_date"]) if check.params.get("min_date") else None
    max_date = pd.to_datetime(check.params["max_date"]) if check.params.get("max_date") else None
    if not_future:
        max_date = pd.Timestamp.now()

    violations = pd.Series(False, index=column.index)
    if min_date is not None:
        violations |= column < min_date
    if max_date is not None:
        violations |= column > max_date

    violation_count = int(violations.sum())
    return violation_count == 0, {"violation_count": violation_count}


@register(CheckType.NO_DUPLICATES_ACROSS_COLUMNS)
def no_duplicates_across_columns(df: pd.DataFrame, check: CheckConfig) -> tuple[bool, dict]:
    columns = check.params["columns"]
    duplicate_count = int(df.duplicated(subset=columns).sum())
    return duplicate_count == 0, {"duplicate_count": duplicate_count, "columns": columns}
