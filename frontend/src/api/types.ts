// Hand-mirrored from backend/checkyourdata/schema.py. Kept in sync manually — small,
// stable list, not worth codegen at this scale.

export const CHECK_TYPES = [
  "not_null",
  "null_percentage_max",
  "unique",
  "uniqueness_percentage_min",
  "min_max_range",
  "allowed_values",
  "regex_match",
  "data_type_check",
  "string_length_range",
  "date_range",
  "no_duplicates_across_columns",
  "mean_within_pct",
  "median_within_pct",
  "std_dev_within_pct",
  "percentile_range",
  "outlier_rate_max",
  "distribution_shift",
  "row_count_min",
  "row_count_max",
  "row_count_change_pct",
  "column_count_match",
  "column_order_match",
  "freshness_check",
  "referential_check",
  "conditional_check",
] as const;

export type CheckType = (typeof CHECK_TYPES)[number];

export const CHECK_CATEGORIES: Record<CheckType, "column" | "statistical" | "table" | "cross_column"> = {
  not_null: "column",
  null_percentage_max: "column",
  unique: "column",
  uniqueness_percentage_min: "column",
  min_max_range: "column",
  allowed_values: "column",
  regex_match: "column",
  data_type_check: "column",
  string_length_range: "column",
  date_range: "column",
  no_duplicates_across_columns: "column",
  mean_within_pct: "statistical",
  median_within_pct: "statistical",
  std_dev_within_pct: "statistical",
  percentile_range: "statistical",
  outlier_rate_max: "statistical",
  distribution_shift: "statistical",
  row_count_min: "table",
  row_count_max: "table",
  row_count_change_pct: "table",
  column_count_match: "table",
  column_order_match: "table",
  freshness_check: "table",
  referential_check: "cross_column",
  conditional_check: "cross_column",
};

// Check types that drift.inject_drift_baselines fills in automatically at run time —
// flagged visually in the history view since a failure here means "drift detected."
export const DRIFT_CHECK_TYPES: ReadonlySet<CheckType> = new Set([
  "mean_within_pct",
  "median_within_pct",
  "std_dev_within_pct",
  "row_count_change_pct",
  "distribution_shift",
]);

// Check types that don't take a `column` (table-level / composite checks).
export const TABLE_LEVEL_CHECK_TYPES: ReadonlySet<CheckType> = new Set([
  "no_duplicates_across_columns",
  "row_count_min",
  "row_count_max",
  "row_count_change_pct",
  "column_count_match",
  "column_order_match",
  "conditional_check",
]);

export type CheckSource = "ai_suggested" | "manual";

export interface CheckConfig {
  column: string | null;
  check_type: CheckType;
  params: Record<string, unknown>;
  source: CheckSource;
  active: boolean;
}

export interface CheckOut extends CheckConfig {
  id: number;
}

export interface DatasetSummary {
  id: number;
  name: string;
  row_count: number;
  column_schema: Record<string, string>;
}

export interface ColumnInfo {
  name: string;
  dtype: string;
}

export interface SchemaResponse {
  columns: ColumnInfo[];
  sample_rows: Record<string, unknown>[];
}

export interface RunResultOut {
  check_id: number;
  column: string | null;
  check_type: CheckType;
  passed: boolean;
  details: Record<string, unknown>;
}

export interface RunResponse {
  run_id: number;
  run_at: string;
  results: RunResultOut[];
}

export interface HistoryEntry {
  run_id: number;
  run_at: string;
  results: RunResultOut[];
}
