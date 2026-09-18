import hashlib
import json
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from checkyourdata.db.models import SchemaCache
from checkyourdata.schema import CheckConfig


def hash_payload(column_schema: dict[str, str], sample_rows: list[dict[str, Any]]) -> str:
    canonical = json.dumps({"columns": column_schema, "sample": sample_rows}, sort_keys=True, default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def get_cached(session: Session, hash_key: str) -> list[CheckConfig] | None:
    stmt = select(SchemaCache).where(SchemaCache.hash == hash_key)
    entry = session.execute(stmt).scalar_one_or_none()
    if entry is None:
        return None
    return [CheckConfig(**c) for c in entry.suggested_checks]


def store_cached(session: Session, hash_key: str, checks: list[CheckConfig]) -> None:
    session.add(SchemaCache(hash=hash_key, suggested_checks=[c.model_dump(mode="json") for c in checks]))
    session.commit()
