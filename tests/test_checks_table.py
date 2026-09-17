import pandas as pd

from checkyourdata.checks.table_checks import (
    column_count_match,
    column_order_match,
    freshness_check,
    row_count_max,
    row_count_min,
)
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


def test_row_count_max_fails_when_exceeded():
    df = pd.DataFrame({"a": [1, 2, 3]})
    check = CheckConfig(check_type=CheckType.ROW_COUNT_MAX, params={"max_rows": 2})

    passed, details = row_count_max(df, check)

    assert passed is False
    assert details["row_count"] == 3


def test_column_count_match_fails_on_mismatch():
    df = pd.DataFrame({"a": [1], "b": [2]})
    check = CheckConfig(check_type=CheckType.COLUMN_COUNT_MATCH, params={"expected_count": 3})

    passed, details = column_count_match(df, check)

    assert passed is False
    assert details["column_count"] == 2


def test_column_order_match_fails_on_reordered_columns():
    df = pd.DataFrame({"b": [1], "a": [2]})
    check = CheckConfig(check_type=CheckType.COLUMN_ORDER_MATCH, params={"expected_columns": ["a", "b"]})

    passed, details = column_order_match(df, check)

    assert passed is False


def test_freshness_check_fails_on_stale_timestamp():
    df = pd.DataFrame({"updated_at": ["2000-01-01T00:00:00"]})
    check = CheckConfig(column="updated_at", check_type=CheckType.FRESHNESS_CHECK, params={"max_age_hours": 24})

    passed, details = freshness_check(df, check)

    assert passed is False
    assert details["age_hours"] > 24
