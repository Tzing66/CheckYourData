from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from checkyourdata import service, storage
from checkyourdata.api.schemas import (
    CheckOut,
    ColumnInfo,
    DatasetSummary,
    HistoryEntry,
    RunResponse,
    RunResultOut,
    SchemaResponse,
)
from checkyourdata.db.models import Check as DBCheck
from checkyourdata.db.models import CheckRun as DBCheckRun
from checkyourdata.db.models import Dataset
from checkyourdata.db.session import get_db
from checkyourdata.schema import CheckConfig

router = APIRouter(prefix="/datasets")


def _get_dataset_or_404(session: Session, dataset_id: int) -> Dataset:
    dataset = session.get(Dataset, dataset_id)
    if dataset is None:
        raise HTTPException(status_code=404, detail=f"Dataset {dataset_id} not found")
    return dataset


@router.post("/upload", response_model=DatasetSummary)
def upload_dataset(file: UploadFile, name: str | None = None, session: Session = Depends(get_db)) -> DatasetSummary:
    contents = file.file.read()
    max_bytes = storage.MAX_UPLOAD_MB * 1024 * 1024
    if len(contents) > max_bytes:
        raise HTTPException(status_code=400, detail=f"File exceeds {storage.MAX_UPLOAD_MB}MB upload limit")

    try:
        df = storage.parse_csv_bytes(contents)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not parse CSV: {e}") from e

    dataset = service.create_dataset(session, name or file.filename or "dataset", df)
    storage.save_upload(dataset.id, contents)

    return DatasetSummary(
        id=dataset.id, name=dataset.name, row_count=dataset.row_count, column_schema=dataset.column_schema
    )


@router.get("/{dataset_id}/schema", response_model=SchemaResponse)
def get_schema(dataset_id: int, session: Session = Depends(get_db)) -> SchemaResponse:
    _get_dataset_or_404(session, dataset_id)
    df = storage.load_dataframe(dataset_id)

    columns = [ColumnInfo(name=c, dtype=str(t)) for c, t in df.dtypes.items()]
    sample_rows = df.head(10).where(df.head(10).notna(), None).to_dict(orient="records")
    return SchemaResponse(columns=columns, sample_rows=sample_rows)


@router.post("/{dataset_id}/suggest-checks")
def suggest_checks(dataset_id: int, session: Session = Depends(get_db)) -> None:
    _get_dataset_or_404(session, dataset_id)
    raise HTTPException(status_code=501, detail="AI check suggestion is implemented in Phase 3")


@router.post("/{dataset_id}/checks", response_model=list[CheckOut])
def post_checks(
    dataset_id: int, checks: list[CheckConfig], session: Session = Depends(get_db)
) -> list[CheckOut]:
    _get_dataset_or_404(session, dataset_id)
    db_checks = service.save_checks(session, dataset_id, checks)
    return [_to_check_out(c) for c in db_checks]


@router.get("/{dataset_id}/checks", response_model=list[CheckOut])
def get_checks(dataset_id: int, session: Session = Depends(get_db)) -> list[CheckOut]:
    _get_dataset_or_404(session, dataset_id)
    db_checks = service.get_active_checks(session, dataset_id)
    return [_to_check_out(c) for c in db_checks]


@router.post("/{dataset_id}/run-checks", response_model=RunResponse)
def run_checks(dataset_id: int, session: Session = Depends(get_db)) -> RunResponse:
    _get_dataset_or_404(session, dataset_id)
    try:
        df = storage.load_dataframe(dataset_id)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"No uploaded data found for dataset {dataset_id}") from e

    check_run, results, check_ids = service.run_checks(session, dataset_id, df)
    return RunResponse(run_id=check_run.id, run_at=check_run.run_at, results=_to_run_results(results, check_ids))


@router.get("/{dataset_id}/history", response_model=list[HistoryEntry])
def get_history(dataset_id: int, session: Session = Depends(get_db)) -> list[HistoryEntry]:
    _get_dataset_or_404(session, dataset_id)

    runs = (
        session.execute(
            select(DBCheckRun).where(DBCheckRun.dataset_id == dataset_id).order_by(DBCheckRun.run_at)
        )
        .scalars()
        .all()
    )

    entries = []
    for run in runs:
        results = [
            RunResultOut(
                check_id=result.check_id,
                column=result.check.column,
                check_type=result.check.check_type,
                passed=result.passed,
                details=result.details,
            )
            for result in run.check_results
        ]
        entries.append(HistoryEntry(run_id=run.id, run_at=run.run_at, results=results))
    return entries


def _to_check_out(check: DBCheck) -> CheckOut:
    return CheckOut(
        id=check.id,
        column=check.column,
        check_type=check.check_type,
        params=check.params,
        source=check.source,
        active=check.active,
    )


def _to_run_results(results, check_ids: dict[tuple[str | None, str], int]) -> list[RunResultOut]:
    return [
        RunResultOut(
            check_id=check_ids[(result.check.column, result.check.check_type.value)],
            column=result.check.column,
            check_type=result.check.check_type,
            passed=result.passed,
            details=result.details,
        )
        for result in results
    ]
