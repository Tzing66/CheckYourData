import pandas as pd

from checkyourdata.checks.cross_column_checks import conditional_check, referential_check
from checkyourdata.schema import CheckConfig, CheckType


def test_referential_check_passes_when_all_values_in_reference():
    df = pd.DataFrame({"country_code": ["US", "IN", "US"]})
    check = CheckConfig(
        column="country_code",
        check_type=CheckType.REFERENTIAL_CHECK,
        params={"reference_values": ["US", "IN", "UK"]},
    )

    passed, details = referential_check(df, check)

    assert passed is True
    assert details["invalid_count"] == 0


def test_referential_check_fails_when_value_not_in_reference():
    df = pd.DataFrame({"country_code": ["US", "XX", "US"]})
    check = CheckConfig(
        column="country_code",
        check_type=CheckType.REFERENTIAL_CHECK,
        params={"reference_values": ["US", "IN", "UK"]},
    )

    passed, details = referential_check(df, check)

    assert passed is False
    assert details["invalid_count"] == 1
    assert "XX" in details["invalid_examples"]


def test_conditional_check_fails_when_then_condition_violated():
    df = pd.DataFrame(
        {
            "status": ["shipped", "shipped", "pending"],
            "tracking_number": ["TRK1", None, None],
        }
    )
    check = CheckConfig(
        check_type=CheckType.CONDITIONAL_CHECK,
        params={
            "if_column": "status",
            "if_value": "shipped",
            "then_column": "tracking_number",
            "then_operator": "not_null",
        },
    )

    passed, details = conditional_check(df, check)

    assert passed is False
    assert details["violation_count"] == 1
    assert details["checked_rows"] == 2


def test_conditional_check_passes_when_then_condition_satisfied():
    df = pd.DataFrame({"status": ["shipped"], "tracking_number": ["TRK1"]})
    check = CheckConfig(
        check_type=CheckType.CONDITIONAL_CHECK,
        params={
            "if_column": "status",
            "if_value": "shipped",
            "then_column": "tracking_number",
            "then_operator": "not_null",
        },
    )

    passed, _ = conditional_check(df, check)

    assert passed is True
