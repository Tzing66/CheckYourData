import json
import os
from typing import Any

import anthropic
from pydantic import ValidationError

from checkyourdata.schema import CheckConfig, CheckSource, CheckType

DEFAULT_MODEL = "claude-haiku-4-5-20251001"
TOOL_NAME = "propose_checks"

# Exact param keys each check_type's implementation expects, shown to the model so it doesn't
# have to guess key names (e.g. "max_pct" not "max_percentage"). Kept next to, not generated
# from, schema.REQUIRED_PARAMS, since this also documents optional keys and the drift-check
# baseline_* note that REQUIRED_PARAMS deliberately omits.
PARAM_HINTS: dict[CheckType, str] = {
    CheckType.NOT_NULL: "{}",
    CheckType.NULL_PERCENTAGE_MAX: "{max_pct: float (0-1)}",
    CheckType.UNIQUE: "{}",
    CheckType.UNIQUENESS_PERCENTAGE_MIN: "{min_pct: float (0-1)}",
    CheckType.MIN_MAX_RANGE: "{min?: number, max?: number}",
    CheckType.ALLOWED_VALUES: "{values: list}",
    CheckType.REGEX_MATCH: "{pattern: string}",
    CheckType.DATA_TYPE_CHECK: '{expected_type: "int"|"float"|"numeric"|"datetime"|"bool"|"string"}',
    CheckType.STRING_LENGTH_RANGE: "{min_length?: int, max_length?: int}",
    CheckType.DATE_RANGE: "{min_date?: string, max_date?: string, not_future?: bool}",
    CheckType.NO_DUPLICATES_ACROSS_COLUMNS: "{columns: list of column names}",
    CheckType.MEAN_WITHIN_PCT: "{pct?: float (0-1)} - baseline is computed automatically, do not supply it",
    CheckType.MEDIAN_WITHIN_PCT: "{pct?: float (0-1)} - baseline is computed automatically, do not supply it",
    CheckType.STD_DEV_WITHIN_PCT: "{pct?: float (0-1)} - baseline is computed automatically, do not supply it",
    CheckType.PERCENTILE_RANGE: "{percentile: float (0-1), min?: number, max?: number}",
    CheckType.OUTLIER_RATE_MAX: "{std_devs?: number, max_rate?: float (0-1)}",
    CheckType.DISTRIBUTION_SHIFT: "{max_psi?: float} - baseline is computed automatically, do not supply it",
    CheckType.ROW_COUNT_MIN: "{min_rows: int}",
    CheckType.ROW_COUNT_MAX: "{max_rows: int}",
    CheckType.ROW_COUNT_CHANGE_PCT: "{pct?: float (0-1)} - baseline is computed automatically, do not supply it",
    CheckType.COLUMN_COUNT_MATCH: "{expected_count: int}",
    CheckType.COLUMN_ORDER_MATCH: "{expected_columns: list of column names in order}",
    CheckType.FRESHNESS_CHECK: "{max_age_hours: number} - column is the timestamp column",
    CheckType.REFERENTIAL_CHECK: "{reference_values: list} - column's values must all appear in this list",
    CheckType.CONDITIONAL_CHECK: (
        "{if_column: string, if_value: any, then_column: string, "
        'then_operator: "equals"|"not_equals"|"gt"|"gte"|"lt"|"lte"|"not_null", then_value?: any} '
        "- table-level, omit column"
    ),
}

SYSTEM_PROMPT = """You are a data quality expert. You will be given a dataset's column \
schema (column name -> pandas dtype) and a small sample of rows. For each column, infer \
its semantic type (e.g. unique id, email, categorical, timestamp, numeric measurement, \
free text) and propose a short, sensible list of data validation checks using ONLY the \
check types listed in the propose_checks tool's check_type enum. You may also propose \
table-level checks (e.g. row_count_min) by omitting "column". Respond ONLY by calling the \
propose_checks tool - do not include any other commentary."""


class AgentSuggestionError(RuntimeError):
    pass


_client: anthropic.Anthropic | None = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _client


def _param_hints_text() -> str:
    return "\n".join(f"- {check_type.value}: {hint}" for check_type, hint in PARAM_HINTS.items())


def _tool_schema() -> dict[str, Any]:
    return {
        "name": TOOL_NAME,
        "description": (
            "Propose data quality checks for the given dataset schema and sample rows. "
            "Each check's params must use exactly the keys shown below for its check_type "
            "(unmarked keys are required, keys ending in ? are optional):\n" + _param_hints_text()
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "checks": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "column": {
                                "type": ["string", "null"],
                                "description": "Column this check applies to, or null for a table-level check.",
                            },
                            "check_type": {
                                "type": "string",
                                "enum": [t.value for t in CheckType],
                            },
                            "params": {
                                "type": "object",
                                "description": "See the tool description for the exact param keys this check_type needs.",
                            },
                        },
                        "required": ["check_type", "params"],
                    },
                },
            },
            "required": ["checks"],
        },
    }


def _call_claude(messages: list[dict]) -> anthropic.types.Message:
    model = os.environ.get("ANTHROPIC_MODEL") or DEFAULT_MODEL
    return _get_client().messages.create(
        model=model,
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=messages,
        tools=[_tool_schema()],
        tool_choice={"type": "tool", "name": TOOL_NAME},
    )


def suggest_checks(
    column_schema: dict[str, str], sample_rows: list[dict[str, Any]], max_attempts: int = 2
) -> list[CheckConfig]:
    user_content = json.dumps({"columns": column_schema, "sample_rows": sample_rows})
    messages: list[dict] = [{"role": "user", "content": user_content}]

    last_error: str | None = None
    for _ in range(max_attempts):
        response = _call_claude(messages)
        tool_use = next((b for b in response.content if getattr(b, "type", None) == "tool_use"), None)

        if tool_use is None:
            last_error = "model did not call the propose_checks tool"
            messages.append({"role": "user", "content": "You must respond by calling the propose_checks tool."})
            continue

        try:
            return [
                CheckConfig(source=CheckSource.AI_SUGGESTED, **item) for item in tool_use.input.get("checks", [])
            ]
        except ValidationError as e:
            last_error = str(e)
            messages.append({"role": "assistant", "content": response.content})
            messages.append(
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": tool_use.id,
                            "content": f"Invalid output: {e}. Call propose_checks again with valid arguments.",
                            "is_error": True,
                        }
                    ],
                }
            )

    raise AgentSuggestionError(f"Claude failed to produce valid checks after {max_attempts} attempts: {last_error}")
