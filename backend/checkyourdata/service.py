import pandas as pd
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from checkyourdata.baseline import inject_drift_baselines, store_run_baseline
from checkyourdata.db.models import Check as DBCheck
from checkyourdata.db.models import CheckResult as DBCheckResult
from checkyourdata.db.models import CheckRun as DBCheckRun
from checkyourdata.db.models import Dataset
from checkyourdata.runner import CheckRunner
from checkyourdata.schema import CheckConfig, CheckResult, CheckSource, CheckType


def create_dataset(session: Session, name: str, df: pd.DataFrame) -> Dataset:
    dataset = Dataset(name=name, column_schema={c: str(t) for c, t in df.dtypes.items()}, row_count=len(df))
    session.add(dataset)
    session.commit()
    return dataset


def save_checks(session: Session, dataset_id: int, checks: list[CheckConfig]) -> list[DBCheck]:
    """Replace the dataset's active check set with the submitted list."""
    session.execute(
        update(DBCheck).where(DBCheck.dataset_id == dataset_id, DBCheck.active.is_(True)).values(active=False)
    )

    db_checks = []
    for check in checks:
        db_check = DBCheck(
            dataset_id=dataset_id,
            column=check.column,
            check_type=check.check_type.value,
            params=check.params,
            source=check.source.value,
            active=True,
        )
        session.add(db_check)
        db_checks.append(db_check)
    session.commit()
    return db_checks


def get_active_checks(session: Session, dataset_id: int) -> list[DBCheck]:
    stmt = select(DBCheck).where(DBCheck.dataset_id == dataset_id, DBCheck.active.is_(True))
    return list(session.execute(stmt).scalars().all())


def run_checks(
    session: Session, dataset_id: int, df: pd.DataFrame
) -> tuple[DBCheckRun, list[CheckResult], dict[tuple[str | None, str], int]]:
    """Run the dataset's active checks against df, persist the run, and refresh the baseline."""
    db_checks = get_active_checks(session, dataset_id)
    check_ids = {(c.column, c.check_type): c.id for c in db_checks}
    configs = [
        CheckConfig(
            column=c.column,
            check_type=CheckType(c.check_type),
            params=c.params,
            source=CheckSource(c.source),
            active=c.active,
        )
        for c in db_checks
    ]

    prepared = inject_drift_baselines(session, dataset_id, configs)
    results = CheckRunner().run(df, prepared)

    check_run = DBCheckRun(dataset_id=dataset_id)
    session.add(check_run)
    session.flush()
    for result in results:
        key = (result.check.column, result.check.check_type.value)
        session.add(
            DBCheckResult(
                check_run_id=check_run.id,
                check_id=check_ids[key],
                passed=result.passed,
                details=result.details,
            )
        )
    session.commit()

    numeric_columns = df.select_dtypes(include="number").columns.tolist()
    store_run_baseline(session, dataset_id, df, numeric_columns)

    return check_run, results, check_ids
