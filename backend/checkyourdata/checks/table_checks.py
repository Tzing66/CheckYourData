import pandas as pd

from checkyourdata.checks.registry import register
from checkyourdata.schema import CheckConfig, CheckType


@register(CheckType.ROW_COUNT_MIN)
def row_count_min(df: pd.DataFrame, check: CheckConfig) -> tuple[bool, dict]:
    min_rows = check.params["min_rows"]
    row_count = len(df)
    return row_count >= min_rows, {"row_count": row_count, "min_rows": min_rows}
