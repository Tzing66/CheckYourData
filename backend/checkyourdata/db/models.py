from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Dataset(Base):
    __tablename__ = "datasets"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    column_schema: Mapped[dict] = mapped_column(JSON, nullable=False)
    row_count: Mapped[int] = mapped_column(nullable=False)
    # Anonymous per-browser id today (X-Client-Id header); a real user id later can
    # reuse this same column unchanged once auth exists. Nullable: rows from before
    # this column existed just won't show up in anyone's list.
    owner_id: Mapped[str | None] = mapped_column(String, nullable=True)

    checks: Mapped[list["Check"]] = relationship(back_populates="dataset")
    check_runs: Mapped[list["CheckRun"]] = relationship(back_populates="dataset")
    baseline_stats: Mapped[list["BaselineStat"]] = relationship(back_populates="dataset")


class Check(Base):
    __tablename__ = "checks"

    id: Mapped[int] = mapped_column(primary_key=True)
    dataset_id: Mapped[int] = mapped_column(ForeignKey("datasets.id"), nullable=False)
    column: Mapped[str | None] = mapped_column(String, nullable=True)
    check_type: Mapped[str] = mapped_column(String, nullable=False)
    params: Mapped[dict] = mapped_column(JSON, default=dict)
    source: Mapped[str] = mapped_column(String, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    dataset: Mapped["Dataset"] = relationship(back_populates="checks")
    check_results: Mapped[list["CheckResult"]] = relationship(back_populates="check")


class CheckRun(Base):
    __tablename__ = "check_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    dataset_id: Mapped[int] = mapped_column(ForeignKey("datasets.id"), nullable=False)
    run_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    dataset: Mapped["Dataset"] = relationship(back_populates="check_runs")
    check_results: Mapped[list["CheckResult"]] = relationship(back_populates="check_run")


class CheckResult(Base):
    __tablename__ = "check_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    check_run_id: Mapped[int] = mapped_column(ForeignKey("check_runs.id"), nullable=False)
    check_id: Mapped[int] = mapped_column(ForeignKey("checks.id"), nullable=False)
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    details: Mapped[dict] = mapped_column(JSON, default=dict)

    check_run: Mapped["CheckRun"] = relationship(back_populates="check_results")
    check: Mapped["Check"] = relationship(back_populates="check_results")


class BaselineStat(Base):
    __tablename__ = "baseline_stats"

    id: Mapped[int] = mapped_column(primary_key=True)
    dataset_id: Mapped[int] = mapped_column(ForeignKey("datasets.id"), nullable=False)
    column: Mapped[str | None] = mapped_column(String, nullable=True)
    stat_type: Mapped[str] = mapped_column(String, nullable=False)
    value: Mapped[dict] = mapped_column(JSON, nullable=False)
    computed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    dataset: Mapped["Dataset"] = relationship(back_populates="baseline_stats")


class SchemaCache(Base):
    __tablename__ = "schema_cache"

    id: Mapped[int] = mapped_column(primary_key=True)
    hash: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    suggested_checks: Mapped[list] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
