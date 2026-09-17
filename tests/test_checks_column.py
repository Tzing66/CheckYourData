import pandas as pd

from checkyourdata.checks.column_checks import min_max_range, not_null
from checkyourdata.schema import CheckConfig, CheckType


def test_not_null_passes_when_no_nulls():
    df = pd.DataFrame({"age": [1, 2, 3]})
    check = CheckConfig(column="age", check_type=CheckType.NOT_NULL)

    passed, details = not_null(df, check)

    assert passed is True
    assert details["null_count"] == 0


def test_not_null_fails_when_nulls_present():
    df = pd.DataFrame({"age": [1, None, 3]})
    check = CheckConfig(column="age", check_type=CheckType.NOT_NULL)

    passed, details = not_null(df, check)

    assert passed is False
    assert details["null_count"] == 1


def test_min_max_range_passes_within_bounds():
    df = pd.DataFrame({"age": [10, 20, 30]})
    check = CheckConfig(column="age", check_type=CheckType.MIN_MAX_RANGE, params={"min": 0, "max": 100})

    passed, details = min_max_range(df, check)

    assert passed is True
    assert details["violation_count"] == 0


def test_min_max_range_fails_outside_bounds():
    df = pd.DataFrame({"age": [10, 200, 30]})
    check = CheckConfig(column="age", check_type=CheckType.MIN_MAX_RANGE, params={"min": 0, "max": 100})

    passed, details = min_max_range(df, check)

    assert passed is False
    assert details["violation_count"] == 1
