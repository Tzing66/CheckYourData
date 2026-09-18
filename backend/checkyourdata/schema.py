from enum import Enum
from typing import Any

from pydantic import BaseModel, model_validator


class CheckCategory(str, Enum):
    COLUMN = "column"
    STATISTICAL = "statistical"
    TABLE = "table"
    CROSS_COLUMN = "cross_column"


class CheckType(str, Enum):
    # Column-level
    NOT_NULL = "not_null"
    NULL_PERCENTAGE_MAX = "null_percentage_max"
    UNIQUE = "unique"
    UNIQUENESS_PERCENTAGE_MIN = "uniqueness_percentage_min"
    MIN_MAX_RANGE = "min_max_range"
    ALLOWED_VALUES = "allowed_values"
    REGEX_MATCH = "regex_match"
    DATA_TYPE_CHECK = "data_type_check"
    STRING_LENGTH_RANGE = "string_length_range"
    DATE_RANGE = "date_range"
    NO_DUPLICATES_ACROSS_COLUMNS = "no_duplicates_across_columns"

    # Distribution / statistical
    MEAN_WITHIN_PCT = "mean_within_pct"
    MEDIAN_WITHIN_PCT = "median_within_pct"
    STD_DEV_WITHIN_PCT = "std_dev_within_pct"
    PERCENTILE_RANGE = "percentile_range"
    OUTLIER_RATE_MAX = "outlier_rate_max"
    DISTRIBUTION_SHIFT = "distribution_shift"

    # Table-level
    ROW_COUNT_MIN = "row_count_min"
    ROW_COUNT_MAX = "row_count_max"
    ROW_COUNT_CHANGE_PCT = "row_count_change_pct"
    COLUMN_COUNT_MATCH = "column_count_match"
    COLUMN_ORDER_MATCH = "column_order_match"
    FRESHNESS_CHECK = "freshness_check"

    # Cross-column
    REFERENTIAL_CHECK = "referential_check"
    CONDITIONAL_CHECK = "conditional_check"


# Check types that require a `column`; table-level checks omit it.
COLUMN_SCOPED_CHECK_TYPES = {
    CheckType.NOT_NULL,
    CheckType.NULL_PERCENTAGE_MAX,
    CheckType.UNIQUE,
    CheckType.UNIQUENESS_PERCENTAGE_MIN,
    CheckType.MIN_MAX_RANGE,
    CheckType.ALLOWED_VALUES,
    CheckType.REGEX_MATCH,
    CheckType.DATA_TYPE_CHECK,
    CheckType.STRING_LENGTH_RANGE,
    CheckType.DATE_RANGE,
    CheckType.MEAN_WITHIN_PCT,
    CheckType.MEDIAN_WITHIN_PCT,
    CheckType.STD_DEV_WITHIN_PCT,
    CheckType.PERCENTILE_RANGE,
    CheckType.OUTLIER_RATE_MAX,
    CheckType.DISTRIBUTION_SHIFT,
    CheckType.FRESHNESS_CHECK,
    CheckType.REFERENTIAL_CHECK,
}

CHECK_TYPE_CATEGORY = {
    CheckType.NOT_NULL: CheckCategory.COLUMN,
    CheckType.NULL_PERCENTAGE_MAX: CheckCategory.COLUMN,
    CheckType.UNIQUE: CheckCategory.COLUMN,
    CheckType.UNIQUENESS_PERCENTAGE_MIN: CheckCategory.COLUMN,
    CheckType.MIN_MAX_RANGE: CheckCategory.COLUMN,
    CheckType.ALLOWED_VALUES: CheckCategory.COLUMN,
    CheckType.REGEX_MATCH: CheckCategory.COLUMN,
    CheckType.DATA_TYPE_CHECK: CheckCategory.COLUMN,
    CheckType.STRING_LENGTH_RANGE: CheckCategory.COLUMN,
    CheckType.DATE_RANGE: CheckCategory.COLUMN,
    CheckType.NO_DUPLICATES_ACROSS_COLUMNS: CheckCategory.COLUMN,
    CheckType.MEAN_WITHIN_PCT: CheckCategory.STATISTICAL,
    CheckType.MEDIAN_WITHIN_PCT: CheckCategory.STATISTICAL,
    CheckType.STD_DEV_WITHIN_PCT: CheckCategory.STATISTICAL,
    CheckType.PERCENTILE_RANGE: CheckCategory.STATISTICAL,
    CheckType.OUTLIER_RATE_MAX: CheckCategory.STATISTICAL,
    CheckType.DISTRIBUTION_SHIFT: CheckCategory.STATISTICAL,
    CheckType.ROW_COUNT_MIN: CheckCategory.TABLE,
    CheckType.ROW_COUNT_MAX: CheckCategory.TABLE,
    CheckType.ROW_COUNT_CHANGE_PCT: CheckCategory.TABLE,
    CheckType.COLUMN_COUNT_MATCH: CheckCategory.TABLE,
    CheckType.COLUMN_ORDER_MATCH: CheckCategory.TABLE,
    CheckType.FRESHNESS_CHECK: CheckCategory.TABLE,
    CheckType.REFERENTIAL_CHECK: CheckCategory.CROSS_COLUMN,
    CheckType.CONDITIONAL_CHECK: CheckCategory.CROSS_COLUMN,
}


class CheckSource(str, Enum):
    AI_SUGGESTED = "ai_suggested"
    MANUAL = "manual"


# Param keys each check implementation reads via params[key] (not params.get(key, default)).
# Drift checks (mean/median/std_dev_within_pct, row_count_change_pct, distribution_shift) need
# baseline_* params too, but those are injected at run time by baseline.inject_drift_baselines —
# callers (including the AI agent) must never supply them directly, so they're excluded here.
REQUIRED_PARAMS: dict[CheckType, set[str]] = {
    CheckType.NOT_NULL: set(),
    CheckType.NULL_PERCENTAGE_MAX: {"max_pct"},
    CheckType.UNIQUE: set(),
    CheckType.UNIQUENESS_PERCENTAGE_MIN: {"min_pct"},
    CheckType.MIN_MAX_RANGE: set(),
    CheckType.ALLOWED_VALUES: {"values"},
    CheckType.REGEX_MATCH: {"pattern"},
    CheckType.DATA_TYPE_CHECK: {"expected_type"},
    CheckType.STRING_LENGTH_RANGE: set(),
    CheckType.DATE_RANGE: set(),
    CheckType.NO_DUPLICATES_ACROSS_COLUMNS: {"columns"},
    CheckType.MEAN_WITHIN_PCT: set(),
    CheckType.MEDIAN_WITHIN_PCT: set(),
    CheckType.STD_DEV_WITHIN_PCT: set(),
    CheckType.PERCENTILE_RANGE: {"percentile"},
    CheckType.OUTLIER_RATE_MAX: set(),
    CheckType.DISTRIBUTION_SHIFT: set(),
    CheckType.ROW_COUNT_MIN: {"min_rows"},
    CheckType.ROW_COUNT_MAX: {"max_rows"},
    CheckType.ROW_COUNT_CHANGE_PCT: set(),
    CheckType.COLUMN_COUNT_MATCH: {"expected_count"},
    CheckType.COLUMN_ORDER_MATCH: {"expected_columns"},
    CheckType.FRESHNESS_CHECK: {"max_age_hours"},
    CheckType.REFERENTIAL_CHECK: {"reference_values"},
    CheckType.CONDITIONAL_CHECK: {"if_column", "if_value", "then_column", "then_operator"},
}


class CheckConfig(BaseModel):
    column: str | None = None
    check_type: CheckType
    params: dict[str, Any] = {}
    source: CheckSource = CheckSource.MANUAL
    active: bool = True

    @model_validator(mode="after")
    def _validate_column_presence(self) -> "CheckConfig":
        requires_column = self.check_type in COLUMN_SCOPED_CHECK_TYPES
        if requires_column and self.column is None:
            raise ValueError(f"check_type '{self.check_type}' requires a 'column'")
        if not requires_column and self.column is not None:
            raise ValueError(f"check_type '{self.check_type}' is table-level and must not set 'column'")
        return self

    @model_validator(mode="after")
    def _validate_required_params(self) -> "CheckConfig":
        missing = REQUIRED_PARAMS.get(self.check_type, set()) - self.params.keys()
        if missing:
            raise ValueError(f"check_type '{self.check_type}' is missing required params: {sorted(missing)}")
        return self

    @property
    def category(self) -> CheckCategory:
        return CHECK_TYPE_CATEGORY[self.check_type]


class CheckResult(BaseModel):
    check: CheckConfig
    passed: bool
    details: dict[str, Any] = {}
