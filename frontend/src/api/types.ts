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

// Mirrors backend/checkyourdata/agent.py's PARAM_HINTS — shown in the manual check editor
// so a param key isn't just a guessing game. Kept in sync manually, same as CHECK_TYPES.
export const PARAM_HINTS: Record<CheckType, string> = {
  not_null: "{}",
  null_percentage_max: "{ max_pct: float (0-1) }",
  unique: "{}",
  uniqueness_percentage_min: "{ min_pct: float (0-1) }",
  min_max_range: "{ min?: number, max?: number }",
  allowed_values: "{ values: [...] }",
  regex_match: "{ pattern: string }",
  data_type_check: '{ expected_type: "int"|"float"|"numeric"|"datetime"|"bool"|"string" }',
  string_length_range: "{ min_length?: int, max_length?: int }",
  date_range: "{ min_date?: string, max_date?: string, not_future?: bool }",
  no_duplicates_across_columns: "{ columns: [\"colA\", \"colB\", ...] }",
  mean_within_pct: "{ pct?: float (0-1) } — baseline is computed automatically, don't supply it",
  median_within_pct: "{ pct?: float (0-1) } — baseline is computed automatically, don't supply it",
  std_dev_within_pct: "{ pct?: float (0-1) } — baseline is computed automatically, don't supply it",
  percentile_range: "{ percentile: float (0-1), min?: number, max?: number }",
  outlier_rate_max: "{ std_devs?: number, max_rate?: float (0-1) }",
  distribution_shift: "{ max_psi?: float } — baseline is computed automatically, don't supply it",
  row_count_min: "{ min_rows: int }",
  row_count_max: "{ max_rows: int }",
  row_count_change_pct: "{ pct?: float (0-1) } — baseline is computed automatically, don't supply it",
  column_count_match: "{ expected_count: int }",
  column_order_match: '{ expected_columns: ["colA", "colB", ...] }',
  freshness_check: "{ max_age_hours: number } — column is the timestamp column",
  referential_check: "{ reference_values: [...] } — column's values must all appear in this list",
  conditional_check:
    '{ if_column, if_value, then_column, then_operator: "equals"|"not_equals"|"gt"|"gte"|"lt"|"lte"|"not_null", then_value? } — table-level',
};

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
  uploaded_at: string;
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
