import pandas as pd

from checkyourdata.checks.registry import register
from checkyourdata.schema import CheckConfig, CheckType


@register(CheckType.OUTLIER_RATE_MAX)
def outlier_rate_max(df: pd.DataFrame, check: CheckConfig) -> tuple[bool, dict]:
    column = df[check.column].dropna()
    std_devs = check.params.get("std_devs", 3)
    max_rate = check.params.get("max_rate", 0.01)

    mean = column.mean()
    std = column.std()
    if std == 0 or pd.isna(std):
        outlier_rate = 0.0
    else:
        outliers = (column - mean).abs() > std_devs * std
        outlier_rate = float(outliers.sum()) / len(column) if len(column) else 0.0

    return outlier_rate <= max_rate, {
        "outlier_rate": outlier_rate,
        "max_rate": max_rate,
        "mean": float(mean) if not pd.isna(mean) else None,
        "std": float(std) if not pd.isna(std) else None,
    }
