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
