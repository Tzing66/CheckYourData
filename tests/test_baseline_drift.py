import pandas as pd
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from checkyourdata.baseline import get_recent_stats, inject_drift_baselines, store_run_baseline
from checkyourdata.checks.statistical_checks import distribution_shift, mean_within_pct, percentile_range
from checkyourdata.checks.table_checks import row_count_change_pct
from checkyourdata.db.models import Base, Dataset
from checkyourdata.schema import CheckConfig, CheckType


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def _make_dataset(session: Session) -> int:
    dataset = Dataset(name="test", column_schema={}, row_count=0)
    session.add(dataset)
    session.commit()
    return dataset.id


def test_mean_within_pct_passes_close_to_baseline():
    df = pd.DataFrame({"age": [30, 31, 29, 30]})
    check = CheckConfig(
        column="age",
        check_type=CheckType.MEAN_WITHIN_PCT,
        params={"baseline_mean": 30, "pct": 0.1},
    )

    passed, details = mean_within_pct(df, check)

    assert passed is True
    assert details["diff_pct"] < 0.1


def test_mean_within_pct_fails_far_from_baseline():
    df = pd.DataFrame({"age": [60, 61, 59, 60]})
    check = CheckConfig(
        column="age",
        check_type=CheckType.MEAN_WITHIN_PCT,
        params={"baseline_mean": 30, "pct": 0.1},
    )

    passed, _ = mean_within_pct(df, check)

    assert passed is False


def test_row_count_change_pct_fails_on_large_shrink():
    df = pd.DataFrame({"a": range(50)})
    check = CheckConfig(
        check_type=CheckType.ROW_COUNT_CHANGE_PCT,
        params={"baseline_row_count": 200, "pct": 0.2},
    )

    passed, details = row_count_change_pct(df, check)

    assert passed is False
    assert details["diff_pct"] > 0.2


def test_percentile_range_checks_bound():
    df = pd.DataFrame({"score": list(range(100))})
    check = CheckConfig(
        column="score",
        check_type=CheckType.PERCENTILE_RANGE,
        params={"percentile": 0.95, "max": 90},
    )

    passed, details = percentile_range(df, check)

    assert passed is False
    assert details["value"] is not None


def test_distribution_shift_flags_shifted_distribution():
    baseline_values = list(range(0, 100))
    shifted_values = list(range(500, 600))

    check = CheckConfig(
        column="value",
        check_type=CheckType.DISTRIBUTION_SHIFT,
        params={"baseline_values": baseline_values, "max_psi": 0.25},
    )
    df = pd.DataFrame({"value": shifted_values})

    passed, details = distribution_shift(df, check)

    assert passed is False
    assert details["psi"] > 0.25


def test_store_and_retrieve_baseline_stats(session):
    dataset_id = _make_dataset(session)
    df = pd.DataFrame({"age": [30, 31, 29, 30, 32]})

    store_run_baseline(session, dataset_id, df, numeric_columns=["age"])

    numeric_history = get_recent_stats(session, dataset_id, "age", "numeric_summary", n=5)
    assert len(numeric_history) == 1
    assert numeric_history[0]["row_count"] == 5

    table_history = get_recent_stats(session, dataset_id, None, "table_summary", n=5)
    assert table_history[0]["row_count"] == 5


def test_inject_drift_baselines_skips_checks_on_first_run(session):
    dataset_id = _make_dataset(session)
    checks = [CheckConfig(column="age", check_type=CheckType.MEAN_WITHIN_PCT, params={"pct": 0.1})]

    prepared = inject_drift_baselines(session, dataset_id, checks)

    assert prepared == []


def test_inject_drift_baselines_fills_baseline_after_prior_run(session):
    dataset_id = _make_dataset(session)
    store_run_baseline(session, dataset_id, pd.DataFrame({"age": [30, 30, 30]}), numeric_columns=["age"])

    checks = [CheckConfig(column="age", check_type=CheckType.MEAN_WITHIN_PCT, params={"pct": 0.1})]
    prepared = inject_drift_baselines(session, dataset_id, checks)

    assert len(prepared) == 1
    assert prepared[0].params["baseline_mean"] == 30
