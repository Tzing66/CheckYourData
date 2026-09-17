import pandas as pd

from checkyourdata.checks.registry import register
from checkyourdata.schema import CheckConfig, CheckType


@register(CheckType.REFERENTIAL_CHECK)
def referential_check(df: pd.DataFrame, check: CheckConfig) -> tuple[bool, dict]:
    column = df[check.column].dropna()
    reference_values = set(check.params["reference_values"])

    invalid_mask = ~column.isin(reference_values)
    invalid_count = int(invalid_mask.sum())
    return invalid_count == 0, {
        "invalid_count": invalid_count,
        "invalid_examples": column[invalid_mask].unique().tolist()[:10],
    }


_CONDITIONAL_OPERATORS = {
    "equals": lambda series, value: series == value,
    "not_equals": lambda series, value: series != value,
    "gt": lambda series, value: series > value,
    "gte": lambda series, value: series >= value,
    "lt": lambda series, value: series < value,
    "lte": lambda series, value: series <= value,
    "not_null": lambda series, _value: series.notna(),
}


@register(CheckType.CONDITIONAL_CHECK)
def conditional_check(df: pd.DataFrame, check: CheckConfig) -> tuple[bool, dict]:
    if_column = check.params["if_column"]
    if_value = check.params["if_value"]
    then_column = check.params["then_column"]
    then_operator = check.params["then_operator"]
    then_value = check.params.get("then_value")

    mask = df[if_column] == if_value
    subset = df.loc[mask, then_column]
    satisfied = _CONDITIONAL_OPERATORS[then_operator](subset, then_value)

    violation_count = int((~satisfied).sum())
    return violation_count == 0, {"violation_count": violation_count, "checked_rows": int(mask.sum())}
