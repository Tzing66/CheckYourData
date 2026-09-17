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
