"""Phase 1 exit-criteria demo: load a CSV, run checks, print pass/fail + drift.

Run two "runs" of two synthetic messy datasets (customers, orders) against
Postgres, showing that:
  - individual check types correctly pass/fail against messy data
  - drift-dependent checks (mean_within_pct, row_count_change_pct,
    distribution_shift) are no-ops on a first run and correctly fire once a
    second run has something to compare against

This uses the same checkyourdata.service functions as the API layer (Phase 2),
so the script and the API exercise identical persistence logic.

Usage:
    docker compose up -d postgres
    cp .env.example .env
    PYTHONPATH=backend uv run python tests/fixtures/generate_messy_data.py
    PYTHONPATH=backend uv run python scripts/demo_run.py
"""

import sys
from pathlib import Path

import pandas as pd
from sqlalchemy.orm import Session

from checkyourdata import service
from checkyourdata.db.session import get_engine, init_db
from checkyourdata.schema import CheckConfig, CheckType

FIXTURES_DIR = Path(__file__).parent.parent / "tests" / "fixtures" / "data"


def print_results(run_label: str, results) -> None:
    print(f"\n--- {run_label} ---")
    for result in results:
        status = "PASS" if result.passed else "FAIL"
        column = f"[{result.check.column}] " if result.check.column else ""
        print(f"  {status}  {column}{result.check.check_type.value}  {result.details}")


def run_dataset_demo(session: Session, name: str, run1_csv: Path, run2_csv: Path, checks: list[CheckConfig]) -> None:
    print(f"\n=== Dataset: {name} ===")

    df1 = pd.read_csv(run1_csv)
    dataset = service.create_dataset(session, name, df1)
    service.save_checks(session, dataset.id, checks)

    # Run 1: drift checks have no history yet, so they're dropped.
    _, results1, _ = service.run_checks(session, dataset.id, df1)
    dropped = len(checks) - len(results1)
    if dropped:
        print(f"  ({dropped} drift-dependent check(s) skipped: no prior run to compare against yet)")
    print_results("Run 1", results1)

    # Run 2: baseline from run 1 now exists, so drift checks are injected and run.
    df2 = pd.read_csv(run2_csv)
    _, results2, _ = service.run_checks(session, dataset.id, df2)
    print_results("Run 2 (drifted)", results2)


def main() -> None:
    init_db()

    with Session(get_engine()) as session:
        customers_checks = [
            CheckConfig(column="customer_id", check_type=CheckType.NOT_NULL),
            CheckConfig(column="age", check_type=CheckType.NULL_PERCENTAGE_MAX, params={"max_pct": 0.1}),
            CheckConfig(column="age", check_type=CheckType.MIN_MAX_RANGE, params={"min": 0, "max": 100}),
            CheckConfig(column="email", check_type=CheckType.REGEX_MATCH, params={"pattern": r"^[^@]+@[^@]+\.[^@]+$"}),
            CheckConfig(
                column="country_code",
                check_type=CheckType.ALLOWED_VALUES,
                params={"values": ["US", "IN", "UK", "DE", "FR"]},
            ),
            CheckConfig(check_type=CheckType.ROW_COUNT_MIN, params={"min_rows": 160}),
            CheckConfig(check_type=CheckType.ROW_COUNT_CHANGE_PCT, params={"pct": 0.15}),
            CheckConfig(column="age", check_type=CheckType.MEAN_WITHIN_PCT, params={"pct": 0.1}),
            CheckConfig(column="age", check_type=CheckType.DISTRIBUTION_SHIFT, params={"max_psi": 0.25}),
        ]
        run_dataset_demo(
            session,
            "customers",
            FIXTURES_DIR / "customers_run1.csv",
            FIXTURES_DIR / "customers_run2.csv",
            customers_checks,
        )

        orders_checks = [
            CheckConfig(column="order_id", check_type=CheckType.NOT_NULL),
            CheckConfig(column="amount", check_type=CheckType.MIN_MAX_RANGE, params={"min": 0, "max": 1000}),
            CheckConfig(column="amount", check_type=CheckType.OUTLIER_RATE_MAX, params={"std_devs": 3, "max_rate": 0.02}),
            CheckConfig(column="order_date", check_type=CheckType.FRESHNESS_CHECK, params={"max_age_hours": 24}),
            CheckConfig(
                column="customer_id",
                check_type=CheckType.REFERENTIAL_CHECK,
                params={"reference_values": pd.read_csv(FIXTURES_DIR / "customers_run1.csv")["customer_id"].tolist()},
            ),
            CheckConfig(
                check_type=CheckType.CONDITIONAL_CHECK,
                params={
                    "if_column": "shipped",
                    "if_value": True,
                    "then_column": "tracking_number",
                    "then_operator": "not_null",
                },
            ),
            CheckConfig(check_type=CheckType.ROW_COUNT_CHANGE_PCT, params={"pct": 0.3}),
            CheckConfig(column="amount", check_type=CheckType.MEAN_WITHIN_PCT, params={"pct": 0.2}),
        ]
        run_dataset_demo(
            session,
            "orders",
            FIXTURES_DIR / "orders_run1.csv",
            FIXTURES_DIR / "orders_run2.csv",
            orders_checks,
        )


if __name__ == "__main__":
    if not FIXTURES_DIR.exists():
        print(f"No fixtures at {FIXTURES_DIR}. Generate them first:")
        print("  PYTHONPATH=backend uv run python tests/fixtures/generate_messy_data.py")
        sys.exit(1)
    main()
