import io
import os

import pandas as pd
from supabase import Client, create_client

MAX_UPLOAD_MB = 20
BUCKET_NAME = "datasets"

_client: Client | None = None


def _get_client() -> Client:
    global _client
    if _client is None:
        _client = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])
    return _client


def _object_path(dataset_id: int) -> str:
    return f"{dataset_id}.csv"


def save_upload(dataset_id: int, contents: bytes) -> None:
    bucket = _get_client().storage.from_(BUCKET_NAME)
    bucket.upload(
        _object_path(dataset_id),
        contents,
        {"content-type": "text/csv", "upsert": "true"},
    )


def load_dataframe(dataset_id: int) -> pd.DataFrame:
    try:
        contents = _get_client().storage.from_(BUCKET_NAME).download(_object_path(dataset_id))
    except Exception as e:
        raise FileNotFoundError(f"No stored data for dataset {dataset_id}: {e}") from e
    return pd.read_csv(io.BytesIO(contents))


def parse_csv_bytes(contents: bytes) -> pd.DataFrame:
    return pd.read_csv(io.BytesIO(contents))


def column_dtypes(df: pd.DataFrame) -> dict[str, str]:
    return {c: str(t) for c, t in df.dtypes.items()}


def sample_records(df: pd.DataFrame, n: int = 15, max_str_len: int = 200) -> list[dict]:
    """A small, JSON-safe sample: NaN -> None, long strings truncated so a stray text
    column doesn't blow up token usage when this is sent to the AI agent.
    """
    sample = df.head(n)
    sample = sample.where(sample.notna(), None)

    def _truncate(value):
        if isinstance(value, str) and len(value) > max_str_len:
            return value[:max_str_len] + "..."
        return value

    return [{k: _truncate(v) for k, v in row.items()} for row in sample.to_dict(orient="records")]
