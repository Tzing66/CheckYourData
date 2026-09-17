import pandas as pd

from checkyourdata.checks.table_checks import row_count_min
from checkyourdata.schema import CheckConfig, CheckType


def test_row_count_min_passes():
    df = pd.DataFrame({"a": [1, 2, 3]})
    check = CheckConfig(check_type=CheckType.ROW_COUNT_MIN, params={"min_rows": 2})

    passed, details = row_count_min(df, check)

    assert passed is True
    assert details["row_count"] == 3


def test_row_count_min_fails():
    df = pd.DataFrame({"a": [1]})
    check = CheckConfig(check_type=CheckType.ROW_COUNT_MIN, params={"min_rows": 2})

    passed, details = row_count_min(df, check)

    assert passed is False
