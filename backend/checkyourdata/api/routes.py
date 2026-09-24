from fastapi import APIRouter, Depends, Header, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from checkyourdata import cache, service, storage
from checkyourdata.agent import AgentSuggestionError
from checkyourdata.agent import suggest_checks as agent_suggest_checks
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
def upload_dataset(
    file: UploadFile,
    name: str | None = None,
    x_client_id: str | None = Header(default=None, alias="X-Client-Id"),
    session: Session = Depends(get_db),
) -> DatasetSummary:
    contents = file.file.read()
    max_bytes = storage.MAX_UPLOAD_MB * 1024 * 1024
    if len(contents) > max_bytes:
        raise HTTPException(status_code=400, detail=f"File exceeds {storage.MAX_UPLOAD_MB}MB upload limit")

    try:
        df = storage.parse_csv_bytes(contents)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not parse CSV: {e}") from e

    dataset = service.create_dataset(session, name or file.filename or "dataset", df, owner_id=x_client_id)
    storage.save_upload(dataset.id, contents)

    return _to_dataset_summary(dataset)


@router.get("", response_model=list[DatasetSummary])
def list_datasets(
    x_client_id: str | None = Header(default=None, alias="X-Client-Id"),
    session: Session = Depends(get_db),
) -> list[DatasetSummary]:
    if not x_client_id:
        return []
    return [_to_dataset_summary(d) for d in service.list_datasets(session, x_client_id)]


@router.get("/{dataset_id}", response_model=DatasetSummary)
def get_dataset(dataset_id: int, session: Session = Depends(get_db)) -> DatasetSummary:
    dataset = _get_dataset_or_404(session, dataset_id)
    return _to_dataset_summary(dataset)


@router.get("/{dataset_id}/schema", response_model=SchemaResponse)
def get_schema(dataset_id: int, session: Session = Depends(get_db)) -> SchemaResponse:
    _get_dataset_or_404(session, dataset_id)
    df = storage.load_dataframe(dataset_id)

    columns = [ColumnInfo(name=c, dtype=t) for c, t in storage.column_dtypes(df).items()]
    return SchemaResponse(columns=columns, sample_rows=storage.sample_records(df))


@router.post("/{dataset_id}/suggest-checks", response_model=list[CheckConfig])
def suggest_checks(dataset_id: int, session: Session = Depends(get_db)) -> list[CheckConfig]:
    _get_dataset_or_404(session, dataset_id)
    df = storage.load_dataframe(dataset_id)

    column_schema = storage.column_dtypes(df)
    sample_rows = storage.sample_records(df)
    hash_key = cache.hash_payload(column_schema, sample_rows)

    cached = cache.get_cached(session, hash_key)
    if cached is not None:
        return cached

    try:
        checks = agent_suggest_checks(column_schema, sample_rows)
    except AgentSuggestionError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e

    cache.store_cached(session, hash_key, checks)
    return checks


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


def _to_dataset_summary(dataset: Dataset) -> DatasetSummary:
    return DatasetSummary(
        id=dataset.id,
        name=dataset.name,
        row_count=dataset.row_count,
        column_schema=dataset.column_schema,
        uploaded_at=dataset.uploaded_at,
    )


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
