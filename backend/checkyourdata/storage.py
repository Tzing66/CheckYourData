import io
from pathlib import Path

import pandas as pd

UPLOADS_DIR = Path("uploads")
MAX_UPLOAD_MB = 20


def dataset_csv_path(dataset_id: int) -> Path:
    return UPLOADS_DIR / f"{dataset_id}.csv"


def save_upload(dataset_id: int, contents: bytes) -> None:
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    dataset_csv_path(dataset_id).write_bytes(contents)


def load_dataframe(dataset_id: int) -> pd.DataFrame:
    return pd.read_csv(dataset_csv_path(dataset_id))


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
