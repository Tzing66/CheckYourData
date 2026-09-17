import pandas as pd

from checkyourdata.runner import CheckRunner
from checkyourdata.schema import CheckConfig, CheckType


def test_runner_executes_mixed_checks_and_reports_pass_fail():
    df = pd.DataFrame({"age": [10, 20, None], "country_code": ["US", "IN", "US"]})
    checks = [
        CheckConfig(column="age", check_type=CheckType.NOT_NULL),
        CheckConfig(column="age", check_type=CheckType.MIN_MAX_RANGE, params={"min": 0, "max": 100}),
        CheckConfig(check_type=CheckType.ROW_COUNT_MIN, params={"min_rows": 2}),
        CheckConfig(
            column="country_code",
            check_type=CheckType.REFERENTIAL_CHECK,
            params={"reference_values": ["US", "IN"]},
        ),
    ]

    results = CheckRunner().run(df, checks)

    assert len(results) == 4
    by_type = {r.check.check_type: r for r in results}
    assert by_type[CheckType.NOT_NULL].passed is False
    assert by_type[CheckType.MIN_MAX_RANGE].passed is True
    assert by_type[CheckType.ROW_COUNT_MIN].passed is True
    assert by_type[CheckType.REFERENTIAL_CHECK].passed is True


def test_runner_raises_on_unregistered_check_type(monkeypatch):
    import checkyourdata.checks.registry as registry_module

    monkeypatch.setattr(registry_module, "_REGISTRY", {})

    df = pd.DataFrame({"age": [1]})
    checks = [CheckConfig(column="age", check_type=CheckType.NOT_NULL)]

    try:
        CheckRunner().run(df, checks)
        assert False, "expected NotImplementedError"
    except NotImplementedError:
        pass
