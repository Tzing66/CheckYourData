import pandas as pd

from checkyourdata.checks.statistical_checks import outlier_rate_max
from checkyourdata.schema import CheckConfig, CheckType


def test_outlier_rate_max_passes_with_no_outliers():
    df = pd.DataFrame({"value": [10, 11, 9, 10, 12, 9, 11]})
    check = CheckConfig(
        column="value",
        check_type=CheckType.OUTLIER_RATE_MAX,
        params={"std_devs": 3, "max_rate": 0.01},
    )

    passed, details = outlier_rate_max(df, check)

    assert passed is True
    assert details["outlier_rate"] == 0.0


def test_outlier_rate_max_fails_with_extreme_outlier():
    df = pd.DataFrame({"value": [10, 11, 9, 10, 12, 9, 11, 10000]})
    check = CheckConfig(
        column="value",
        check_type=CheckType.OUTLIER_RATE_MAX,
        params={"std_devs": 2, "max_rate": 0.01},
    )

    passed, details = outlier_rate_max(df, check)

    assert passed is False
    assert details["outlier_rate"] > 0.0
