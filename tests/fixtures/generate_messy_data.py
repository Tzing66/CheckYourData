"""Generates synthetic messy datasets (2 "runs" each) used by scripts/demo_run.py
to demonstrate check failures and drift detection without depending on Kaggle.
"""

from pathlib import Path

import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).parent / "data"


def generate_customers_run1(seed: int = 0, n: int = 200) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    customer_id = np.arange(1, n + 1)
    age = rng.normal(loc=35, scale=12, size=n).round().astype(float)
    age[rng.choice(n, size=int(n * 0.05), replace=False)] = np.nan
    age[rng.choice(n, size=3, replace=False)] = 150  # blatant outliers

    email = [f"user{i}@example.com" for i in customer_id]
    for i in rng.choice(n, size=int(n * 0.03), replace=False):
        email[i] = f"user{i}_at_example.com"  # malformed, no "@"

    signup_date = pd.Timestamp.now() - pd.to_timedelta(rng.integers(1, 1000, size=n), unit="D")
    country_code = rng.choice(["US", "IN", "UK", "DE", "FR"], size=n, p=[0.4, 0.25, 0.15, 0.1, 0.1])
    status = rng.choice(["active", "inactive"], size=n, p=[0.8, 0.2])

    return pd.DataFrame(
        {
            "customer_id": customer_id,
            "email": email,
            "age": age,
            "signup_date": signup_date.strftime("%Y-%m-%dT%H:%M:%S"),
            "country_code": country_code,
            "status": status,
        }
    )


def generate_customers_run2(run1: pd.DataFrame, seed: int = 1) -> pd.DataFrame:
    """A later, drifted snapshot: shrinks, more nulls, and an age mean shift."""
    rng = np.random.default_rng(seed)
    n = len(run1)

    kept = rng.choice(n, size=int(n * 0.75), replace=False)
    df = run1.iloc[sorted(kept)].reset_index(drop=True).copy()

    df["age"] = df["age"] + 20
    extra_nulls = rng.choice(len(df), size=int(len(df) * 0.15), replace=False)
    df.loc[extra_nulls, "age"] = np.nan

    df.loc[0, "signup_date"] = (pd.Timestamp.now() + pd.Timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%S")
    return df


def generate_orders_run1(customers: pd.DataFrame, seed: int = 0, n: int = 500) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    order_id = np.arange(1, n + 1)
    customer_id = rng.choice(customers["customer_id"], size=n)
    amount = rng.lognormal(mean=3.5, sigma=0.4, size=n).round(2)
    amount[rng.choice(n, size=5, replace=False)] = 5000.0  # extreme outliers

    order_date = pd.Timestamp.now() - pd.to_timedelta(rng.integers(0, 30 * 24, size=n), unit="h")
    shipped = rng.choice([True, False], size=n, p=[0.7, 0.3])
    tracking_number = [f"TRK-{i:06d}" if s else None for i, s in zip(order_id, shipped)]
    for i in rng.choice(np.where(shipped)[0], size=5, replace=False):
        tracking_number[i] = None  # a few shipped orders missing tracking, on purpose

    return pd.DataFrame(
        {
            "order_id": order_id,
            "customer_id": customer_id,
            "amount": amount,
            "order_date": order_date.strftime("%Y-%m-%dT%H:%M:%S"),
            "shipped": shipped,
            "tracking_number": tracking_number,
        }
    )


def generate_orders_run2(run1: pd.DataFrame, customers: pd.DataFrame, seed: int = 1) -> pd.DataFrame:
    """A later run: order volume spikes, amount distribution shifts up, data goes stale,
    and a few orders reference customers that don't exist.
    """
    rng = np.random.default_rng(seed)
    n = int(len(run1) * 1.6)  # volume spike

    order_id = np.arange(1, n + 1)
    customer_id = rng.choice(customers["customer_id"], size=n).astype(object)
    bad_customer_ids = rng.choice(n, size=4, replace=False)
    customer_id[bad_customer_ids] = customers["customer_id"].max() + rng.integers(1, 1000, size=4)

    amount = rng.lognormal(mean=4.5, sigma=0.4, size=n).round(2)  # shifted up
    order_date = pd.Timestamp.now() - pd.to_timedelta(60 * 24 + rng.integers(0, 24, size=n), unit="h")  # stale
    shipped = rng.choice([True, False], size=n, p=[0.7, 0.3])
    tracking_number = [f"TRK-{i:06d}" if s else None for i, s in zip(order_id, shipped)]

    return pd.DataFrame(
        {
            "order_id": order_id,
            "customer_id": customer_id,
            "amount": amount,
            "order_date": order_date.strftime("%Y-%m-%dT%H:%M:%S"),
            "shipped": shipped,
            "tracking_number": tracking_number,
        }
    )


def write_all() -> None:
    DATA_DIR.mkdir(exist_ok=True)

    customers_run1 = generate_customers_run1()
    customers_run2 = generate_customers_run2(customers_run1)
    orders_run1 = generate_orders_run1(customers_run1)
    orders_run2 = generate_orders_run2(orders_run1, customers_run1)

    customers_run1.to_csv(DATA_DIR / "customers_run1.csv", index=False)
    customers_run2.to_csv(DATA_DIR / "customers_run2.csv", index=False)
    orders_run1.to_csv(DATA_DIR / "orders_run1.csv", index=False)
    orders_run2.to_csv(DATA_DIR / "orders_run2.csv", index=False)


if __name__ == "__main__":
    write_all()
    print(f"Wrote synthetic messy datasets to {DATA_DIR}")
