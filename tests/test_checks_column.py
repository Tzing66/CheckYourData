import pandas as pd

from checkyourdata.checks.column_checks import (
    allowed_values,
    data_type_check,
    date_range,
    min_max_range,
    no_duplicates_across_columns,
    not_null,
    null_percentage_max,
    regex_match,
    string_length_range,
    unique,
    uniqueness_percentage_min,
)
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


def test_null_percentage_max_fails_above_threshold():
    df = pd.DataFrame({"age": [1, None, None, 4]})
    check = CheckConfig(column="age", check_type=CheckType.NULL_PERCENTAGE_MAX, params={"max_pct": 0.25})

    passed, details = null_percentage_max(df, check)

    assert passed is False
    assert details["null_pct"] == 0.5


def test_unique_fails_on_duplicate():
    df = pd.DataFrame({"id": [1, 2, 2, 3]})
    check = CheckConfig(column="id", check_type=CheckType.UNIQUE)

    passed, details = unique(df, check)

    assert passed is False
    assert details["duplicate_count"] == 1


def test_uniqueness_percentage_min_passes_above_threshold():
    df = pd.DataFrame({"id": [1, 2, 3, 3]})
    check = CheckConfig(column="id", check_type=CheckType.UNIQUENESS_PERCENTAGE_MIN, params={"min_pct": 0.7})

    passed, details = uniqueness_percentage_min(df, check)

    assert passed is True
    assert details["uniqueness_pct"] == 0.75


def test_allowed_values_fails_on_unlisted_value():
    df = pd.DataFrame({"status": ["active", "inactive", "bogus"]})
    check = CheckConfig(column="status", check_type=CheckType.ALLOWED_VALUES, params={"values": ["active", "inactive"]})

    passed, details = allowed_values(df, check)

    assert passed is False
    assert details["invalid_count"] == 1


def test_regex_match_fails_on_invalid_email():
    df = pd.DataFrame({"email": ["a@b.com", "not-an-email"]})
    check = CheckConfig(column="email", check_type=CheckType.REGEX_MATCH, params={"pattern": r"^[^@]+@[^@]+\.[^@]+$"})

    passed, details = regex_match(df, check)

    assert passed is False
    assert details["non_matching_count"] == 1


def test_data_type_check_flags_non_numeric_value():
    df = pd.DataFrame({"age": ["30", "31", "thirty-two"]})
    check = CheckConfig(column="age", check_type=CheckType.DATA_TYPE_CHECK, params={"expected_type": "numeric"})

    passed, details = data_type_check(df, check)

    assert passed is False
    assert details["failure_count"] == 1


def test_string_length_range_fails_outside_bounds():
    df = pd.DataFrame({"code": ["AB", "ABC", "A"]})
    check = CheckConfig(
        column="code", check_type=CheckType.STRING_LENGTH_RANGE, params={"min_length": 2, "max_length": 3}
    )

    passed, details = string_length_range(df, check)

    assert passed is False
    assert details["violation_count"] == 1


def test_date_range_flags_future_date():
    df = pd.DataFrame({"event_date": ["2020-01-01", "2999-01-01"]})
    check = CheckConfig(column="event_date", check_type=CheckType.DATE_RANGE, params={"not_future": True})

    passed, details = date_range(df, check)

    assert passed is False
    assert details["violation_count"] == 1


def test_no_duplicates_across_columns_fails_on_composite_duplicate():
    df = pd.DataFrame({"user_id": [1, 1, 2], "order_id": [10, 10, 20]})
    check = CheckConfig(check_type=CheckType.NO_DUPLICATES_ACROSS_COLUMNS, params={"columns": ["user_id", "order_id"]})

    passed, details = no_duplicates_across_columns(df, check)

    assert passed is False
    assert details["duplicate_count"] == 1
