from datetime import datetime
from typing import Any

from pydantic import BaseModel

from checkyourdata.schema import CheckType


class DatasetSummary(BaseModel):
    id: int
    name: str
    row_count: int
    column_schema: dict[str, str]


class ColumnInfo(BaseModel):
    name: str
    dtype: str


class SchemaResponse(BaseModel):
    columns: list[ColumnInfo]
    sample_rows: list[dict[str, Any]]


class CheckOut(BaseModel):
    id: int
    column: str | None
    check_type: CheckType
    params: dict[str, Any]
    source: str
    active: bool


class RunResultOut(BaseModel):
    check_id: int
    column: str | None
    check_type: CheckType
    passed: bool
    details: dict[str, Any]


class RunResponse(BaseModel):
    run_id: int
    run_at: datetime
    results: list[RunResultOut]


class HistoryEntry(BaseModel):
    run_id: int
    run_at: datetime
    results: list[RunResultOut]
