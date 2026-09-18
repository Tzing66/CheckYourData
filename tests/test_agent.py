from types import SimpleNamespace

import pytest

from checkyourdata.agent import AgentSuggestionError, suggest_checks
from checkyourdata.schema import CheckSource, CheckType

COLUMN_SCHEMA = {"customer_id": "int64", "age": "float64"}
SAMPLE_ROWS = [{"customer_id": 1, "age": 30.0}, {"customer_id": 2, "age": 40.0}]


def _tool_use_response(input_data: dict, tool_use_id: str = "toolu_1") -> SimpleNamespace:
    return SimpleNamespace(
        content=[SimpleNamespace(type="tool_use", id=tool_use_id, input=input_data)]
    )


def test_suggest_checks_returns_parsed_checks_on_valid_response(monkeypatch):
    valid_input = {
        "checks": [
            {"column": "customer_id", "check_type": "not_null", "params": {}},
            {"column": "age", "check_type": "min_max_range", "params": {"min": 0, "max": 120}},
        ]
    }
    monkeypatch.setattr("checkyourdata.agent._call_claude", lambda messages: _tool_use_response(valid_input))

    checks = suggest_checks(COLUMN_SCHEMA, SAMPLE_ROWS)

    assert len(checks) == 2
    assert checks[0].check_type == CheckType.NOT_NULL
    assert checks[0].column == "customer_id"
    assert checks[0].source == CheckSource.AI_SUGGESTED
    assert checks[1].params == {"min": 0, "max": 120}


def test_suggest_checks_retries_after_invalid_response_then_succeeds(monkeypatch):
    invalid_input = {"checks": [{"column": "age", "check_type": "not_a_real_check_type", "params": {}}]}
    valid_input = {"checks": [{"column": "age", "check_type": "not_null", "params": {}}]}
    responses = [_tool_use_response(invalid_input), _tool_use_response(valid_input)]

    calls = []

    def fake_call(messages):
        calls.append(messages)
        return responses.pop(0)

    monkeypatch.setattr("checkyourdata.agent._call_claude", fake_call)

    checks = suggest_checks(COLUMN_SCHEMA, SAMPLE_ROWS)

    assert len(checks) == 1
    assert checks[0].check_type == CheckType.NOT_NULL
    assert len(calls) == 2  # confirms a retry actually happened


def test_suggest_checks_raises_after_max_attempts_exhausted(monkeypatch):
    invalid_input = {"checks": [{"column": "age", "check_type": "not_a_real_check_type", "params": {}}]}
    monkeypatch.setattr("checkyourdata.agent._call_claude", lambda messages: _tool_use_response(invalid_input))

    with pytest.raises(AgentSuggestionError):
        suggest_checks(COLUMN_SCHEMA, SAMPLE_ROWS, max_attempts=2)


def test_suggest_checks_retries_when_model_skips_the_tool(monkeypatch):
    valid_input = {"checks": [{"column": "age", "check_type": "not_null", "params": {}}]}
    responses = [SimpleNamespace(content=[SimpleNamespace(type="text", text="no thanks")]), _tool_use_response(valid_input)]

    monkeypatch.setattr("checkyourdata.agent._call_claude", lambda messages: responses.pop(0))

    checks = suggest_checks(COLUMN_SCHEMA, SAMPLE_ROWS)

    assert len(checks) == 1
