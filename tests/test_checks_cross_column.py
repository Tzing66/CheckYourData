import pandas as pd

from checkyourdata.checks.cross_column_checks import referential_check
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
