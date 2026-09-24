import os
from collections.abc import Iterator

from dotenv import load_dotenv
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from checkyourdata.db.models import Base

# Lightweight, idempotent schema evolution for existing tables — Base.metadata.create_all()
# only creates *missing* tables, it never alters ones that already exist in a live database.
# Not a substitute for Alembic once the schema is changing often; fine for one column at a time.
_MIGRATIONS = [
    "ALTER TABLE datasets ADD COLUMN IF NOT EXISTS owner_id VARCHAR",
]

load_dotenv()

_engine: Engine | None = None
_SessionLocal: sessionmaker[Session] | None = None


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        database_url = os.environ["DATABASE_URL"]
        _engine = create_engine(database_url)
    return _engine


def get_session() -> Session:
    global _SessionLocal
    if _SessionLocal is None:
        # expire_on_commit=False: routes commonly read ORM object attributes after
        # commit() to build the API response. With the default (True), every one of
        # those reads on an expired object triggers its own fresh SELECT — for a
        # response built from N rows, that's N extra round-trips (measured: 33s for
        # 87 objects on a remote pooled connection, vs ~0s with this set).
        _SessionLocal = sessionmaker(bind=get_engine(), expire_on_commit=False)
    return _SessionLocal()


def init_db() -> None:
    Base.metadata.create_all(get_engine())
    with get_engine().begin() as conn:
        for statement in _MIGRATIONS:
            conn.execute(text(statement))


def get_db() -> Iterator[Session]:
    session = get_session()
    try:
        yield session
    finally:
        session.close()
