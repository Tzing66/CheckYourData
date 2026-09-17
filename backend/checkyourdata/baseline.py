import numpy as np
import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from checkyourdata.db.models import BaselineStat
from checkyourdata.schema import CheckConfig, CheckType

DRIFT_SAMPLE_SIZE = 1000


def compute_numeric_stats(df: pd.DataFrame, column: str) -> dict:
    series = df[column].dropna()
    return {
        "mean": float(series.mean()) if not series.empty else None,
        "std": float(series.std()) if not series.empty else None,
        "median": float(series.median()) if not series.empty else None,
        "row_count": int(len(series)),
    }


def compute_table_stats(df: pd.DataFrame) -> dict:
    return {"row_count": int(len(df))}


def _psi_bucket_edges(baseline: pd.Series, n_buckets: int = 10) -> np.ndarray:
    quantiles = np.linspace(0, 1, n_buckets + 1)
    edges = np.unique(baseline.quantile(quantiles).to_numpy())
    edges[0] = -np.inf
    edges[-1] = np.inf
    return edges


def population_stability_index(baseline: pd.Series, current: pd.Series, n_buckets: int = 10) -> float:
    """Population Stability Index between a baseline sample and a current sample.

    PSI < 0.1: no significant shift. 0.1-0.25: moderate shift. > 0.25: major shift.
    """
    baseline = baseline.dropna()
    current = current.dropna()
    if baseline.empty or current.empty:
        return 0.0

    edges = _psi_bucket_edges(baseline, n_buckets)
    if len(edges) < 3:
        return 0.0

    baseline_counts = pd.cut(baseline, bins=edges).value_counts(sort=False)
    current_counts = pd.cut(current, bins=edges).value_counts(sort=False)

    baseline_pct = (baseline_counts / len(baseline)).replace(0, 1e-6)
    current_pct = (current_counts / len(current)).replace(0, 1e-6)

    return float(((current_pct - baseline_pct) * np.log(current_pct / baseline_pct)).sum())


def store_run_baseline(session: Session, dataset_id: int, df: pd.DataFrame, numeric_columns: list[str]) -> None:
    """Persist this run's stats so future runs have something to compare against."""
    for column in numeric_columns:
        series = df[column].dropna()
        session.add(
            BaselineStat(
                dataset_id=dataset_id,
                column=column,
                stat_type="numeric_summary",
                value=compute_numeric_stats(df, column),
            )
        )
        sample = series if len(series) <= DRIFT_SAMPLE_SIZE else series.sample(DRIFT_SAMPLE_SIZE, random_state=0)
        session.add(
            BaselineStat(
                dataset_id=dataset_id,
                column=column,
                stat_type="sample",
                value={"values": sample.tolist()},
            )
        )

    session.add(
        BaselineStat(
            dataset_id=dataset_id,
            column=None,
            stat_type="table_summary",
            value=compute_table_stats(df),
        )
    )
    session.commit()


def get_recent_stats(session: Session, dataset_id: int, column: str | None, stat_type: str, n: int = 5) -> list[dict]:
    stmt = (
        select(BaselineStat.value)
        .where(
            BaselineStat.dataset_id == dataset_id,
            BaselineStat.column == column,
            BaselineStat.stat_type == stat_type,
        )
        .order_by(BaselineStat.computed_at.desc())
        .limit(n)
    )
    return [row[0] for row in session.execute(stmt).all()]


_DRIFT_STAT_KEY = {
    CheckType.MEAN_WITHIN_PCT: "mean",
    CheckType.MEDIAN_WITHIN_PCT: "median",
    CheckType.STD_DEV_WITHIN_PCT: "std",
}


def inject_drift_baselines(session: Session, dataset_id: int, checks: list[CheckConfig]) -> list[CheckConfig]:
    """Fill in baseline_* params for drift-dependent checks from run history.

    A drift check is dropped (not run) when no prior run exists yet for its
    dataset/column, since there is nothing to compare against on a first run.
    """
    prepared: list[CheckConfig] = []

    for check in checks:
        if check.check_type in _DRIFT_STAT_KEY:
            stat_key = _DRIFT_STAT_KEY[check.check_type]
            n_runs = check.params.get("n_runs", 5)
            recent = get_recent_stats(session, dataset_id, check.column, "numeric_summary", n_runs)
            values = [r[stat_key] for r in recent if r.get(stat_key) is not None]
            if not values:
                continue
            baseline = sum(values) / len(values)
            prepared.append(check.model_copy(update={"params": {**check.params, f"baseline_{stat_key}": baseline}}))

        elif check.check_type == CheckType.ROW_COUNT_CHANGE_PCT:
            n_runs = check.params.get("n_runs", 5)
            recent = get_recent_stats(session, dataset_id, None, "table_summary", n_runs)
            values = [r["row_count"] for r in recent]
            if not values:
                continue
            baseline = sum(values) / len(values)
            prepared.append(check.model_copy(update={"params": {**check.params, "baseline_row_count": baseline}}))

        elif check.check_type == CheckType.DISTRIBUTION_SHIFT:
            recent = get_recent_stats(session, dataset_id, check.column, "sample", 1)
            if not recent:
                continue
            prepared.append(check.model_copy(update={"params": {**check.params, "baseline_values": recent[0]["values"]}}))

        else:
            prepared.append(check)

    return prepared
