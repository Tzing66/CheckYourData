import type { CheckType, RunResultOut } from "../api/types";

function pct(value: unknown): string {
  return typeof value === "number" ? `${(value * 100).toFixed(1)}%` : String(value);
}

function num(value: unknown): string {
  if (typeof value !== "number") return String(value);
  return Number.isInteger(value) ? String(value) : value.toFixed(2);
}

function plural(count: unknown, noun: string): string {
  const n = typeof count === "number" ? count : 0;
  return `${n} ${noun}${n === 1 ? "" : "s"}`;
}

type Describer = (details: Record<string, unknown>) => { pass: string; fail: string };

const DESCRIBERS: Partial<Record<CheckType, Describer>> = {
  not_null: (d) => ({
    pass: `No missing values across ${num(d.row_count)} rows.`,
    fail: `${plural(d.null_count, "missing value")} found out of ${num(d.row_count)} rows.`,
  }),
  null_percentage_max: (d) => ({
    pass: `Missing value rate (${pct(d.null_pct)}) is within the allowed ${pct(d.max_pct)}.`,
    fail: `Missing value rate is ${pct(d.null_pct)}, above the allowed ${pct(d.max_pct)}.`,
  }),
  unique: (d) => ({
    pass: "All values are unique.",
    fail: `${plural(d.duplicate_count, "duplicate value")} found.`,
  }),
  uniqueness_percentage_min: (d) => ({
    pass: `${pct(d.uniqueness_pct)} of values are unique, meeting the ${pct(d.min_pct)} minimum.`,
    fail: `Only ${pct(d.uniqueness_pct)} of values are unique, below the ${pct(d.min_pct)} minimum.`,
  }),
  min_max_range: (d) => ({
    pass: `All values fall within range (observed ${num(d.observed_min)}–${num(d.observed_max)}).`,
    fail: `${plural(d.violation_count, "value")} fell outside the expected range (observed ${num(d.observed_min)}–${num(d.observed_max)}).`,
  }),
  allowed_values: (d) => ({
    pass: "All values are from the allowed list.",
    fail: `${plural(d.invalid_count, "value")} not on the allowed list.`,
  }),
  regex_match: (d) => ({
    pass: "All values match the expected pattern.",
    fail: `${plural(d.non_matching_count, "value")} didn't match the expected pattern.`,
  }),
  data_type_check: (d) => ({
    pass: `All values are valid ${d.expected_type}.`,
    fail: `${plural(d.failure_count, "value")} not a valid ${d.expected_type}.`,
  }),
  string_length_range: (d) => ({
    pass: "All values have an acceptable length.",
    fail: `${plural(d.violation_count, "value")} outside the expected length.`,
  }),
  date_range: (d) => ({
    pass: "All dates are within the expected range.",
    fail: `${plural(d.violation_count, "date")} outside the expected range.`,
  }),
  no_duplicates_across_columns: (d) => ({
    pass: "No duplicate combinations found.",
    fail: `${plural(d.duplicate_count, "duplicate combination")} found.`,
  }),
  mean_within_pct: (d) => ({
    pass: `Mean (${num(d.current)}) is close to the historical baseline (${num(d.baseline)}).`,
    fail: `Mean has drifted to ${num(d.current)} from a baseline of ${num(d.baseline)} (${pct(d.diff_pct)} change).`,
  }),
  median_within_pct: (d) => ({
    pass: `Median (${num(d.current)}) is close to the historical baseline (${num(d.baseline)}).`,
    fail: `Median has drifted to ${num(d.current)} from a baseline of ${num(d.baseline)} (${pct(d.diff_pct)} change).`,
  }),
  std_dev_within_pct: (d) => ({
    pass: `Spread of values is close to the historical baseline.`,
    fail: `Spread of values has drifted from the historical baseline (${pct(d.diff_pct)} change).`,
  }),
  percentile_range: (d) => ({
    pass: `The ${pct(d.percentile)} percentile (${num(d.value)}) is within range.`,
    fail: `The ${pct(d.percentile)} percentile (${num(d.value)}) is outside the expected range.`,
  }),
  outlier_rate_max: (d) => ({
    pass: `Outlier rate (${pct(d.outlier_rate)}) is within the allowed ${pct(d.max_rate)}.`,
    fail: `Outlier rate (${pct(d.outlier_rate)}) exceeds the allowed ${pct(d.max_rate)}.`,
  }),
  distribution_shift: () => ({
    pass: "Distribution looks stable compared to history.",
    fail: "Distribution has shifted significantly compared to history.",
  }),
  row_count_min: (d) => ({
    pass: `Row count (${num(d.row_count)}) meets the minimum of ${num(d.min_rows)}.`,
    fail: `Row count (${num(d.row_count)}) is below the minimum of ${num(d.min_rows)}.`,
  }),
  row_count_max: (d) => ({
    pass: `Row count (${num(d.row_count)}) is within the maximum of ${num(d.max_rows)}.`,
    fail: `Row count (${num(d.row_count)}) exceeds the maximum of ${num(d.max_rows)}.`,
  }),
  row_count_change_pct: (d) => ({
    pass: "Row count is stable compared to history.",
    fail: `Row count changed significantly — ${num(d.row_count)} now vs ${num(d.baseline_row_count)} before.`,
  }),
  column_count_match: (d) => ({
    pass: `Column count matches the expected ${num(d.expected_count)}.`,
    fail: `Column count is ${num(d.column_count)}, expected ${num(d.expected_count)}.`,
  }),
  column_order_match: () => ({
    pass: "Column order matches what was expected.",
    fail: "Column order doesn't match what was expected.",
  }),
  freshness_check: (d) => ({
    pass: `Most recent record is ${num(d.age_hours)}h old, within the ${num(d.max_age_hours)}h freshness window.`,
    fail: `Most recent record is ${num(d.age_hours)}h old — older than the ${num(d.max_age_hours)}h freshness window.`,
  }),
  referential_check: (d) => ({
    pass: "All values reference a valid entry.",
    fail: `${plural(d.invalid_count, "value")} didn't match any valid reference.`,
  }),
  conditional_check: (d) => ({
    pass: `The condition held for all ${num(d.checked_rows)} matching row(s).`,
    fail: `${plural(d.violation_count, "row")} out of ${num(d.checked_rows)} matching rows violated the condition.`,
  }),
};

/** A short, plain-English summary of a check result — the JSON `details` stays available
 * behind an optional disclosure for anyone who wants the raw numbers. */
export function describeResult(result: RunResultOut): string {
  const describer = DESCRIBERS[result.check_type];
  if (!describer) return result.passed ? "Check passed." : "Check failed.";
  const { pass, fail } = describer(result.details);
  return result.passed ? pass : fail;
}

/** "min_max_range" -> "Min max range" — a readable label instead of raw snake_case. */
export function formatCheckTypeLabel(checkType: string): string {
  const words = checkType.split("_");
  return words[0].charAt(0).toUpperCase() + words[0].slice(1) + (words.length > 1 ? " " + words.slice(1).join(" ") : "");
}
