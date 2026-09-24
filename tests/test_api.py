import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from checkyourdata import storage
from checkyourdata.api.main import app
from checkyourdata.db.models import Base
from checkyourdata.db.session import get_db

CSV_CONTENT = b"id,age\n1,20\n2,30\n3,40\n"


@pytest.fixture
def client(monkeypatch):
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    testing_session_local = sessionmaker(bind=engine)

    def override_get_db():
        session = testing_session_local()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    monkeypatch.setattr("checkyourdata.api.main.init_db", lambda: None)

    # In-memory fake for Supabase Storage — no real network calls in the test suite,
    # same pattern as mocking the Claude call in tests/test_agent.py.
    fake_storage: dict[int, bytes] = {}

    def fake_save_upload(dataset_id: int, contents: bytes) -> None:
        fake_storage[dataset_id] = contents

    def fake_load_dataframe(dataset_id: int):
        if dataset_id not in fake_storage:
            raise FileNotFoundError(f"No stored data for dataset {dataset_id}")
        return storage.parse_csv_bytes(fake_storage[dataset_id])

    monkeypatch.setattr(storage, "save_upload", fake_save_upload)
    monkeypatch.setattr(storage, "load_dataframe", fake_load_dataframe)

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def upload(client: TestClient, content: bytes = CSV_CONTENT, name: str = "test", client_id: str | None = None) -> dict:
    headers = {"X-Client-Id": client_id} if client_id else {}
    response = client.post(
        f"/datasets/upload?name={name}",
        files={"file": ("test.csv", content, "text/csv")},
        headers=headers,
    )
    assert response.status_code == 200, response.text
    return response.json()


def test_upload_and_get_dataset(client: TestClient):
    dataset = upload(client)
    assert dataset["name"] == "test"
    assert dataset["row_count"] == 3
    assert set(dataset["column_schema"].keys()) == {"id", "age"}

    response = client.get(f"/datasets/{dataset['id']}")
    assert response.status_code == 200
    assert response.json() == dataset


def test_list_datasets_scoped_by_client_id(client: TestClient):
    upload(client, name="alice_1", client_id="alice")
    upload(client, name="alice_2", client_id="alice")
    upload(client, name="bob_1", client_id="bob")

    response = client.get("/datasets", headers={"X-Client-Id": "alice"})
    assert response.status_code == 200
    names = {d["name"] for d in response.json()}
    assert names == {"alice_1", "alice_2"}


def test_list_datasets_without_client_id_returns_empty(client: TestClient):
    upload(client, client_id="someone")

    response = client.get("/datasets")
    assert response.status_code == 200
    assert response.json() == []


def test_upload_and_schema(client: TestClient):
    dataset = upload(client)

    response = client.get(f"/datasets/{dataset['id']}/schema")
    assert response.status_code == 200
    body = response.json()
    assert {c["name"] for c in body["columns"]} == {"id", "age"}
    assert len(body["sample_rows"]) == 3


def test_upload_rejects_oversized_file(client: TestClient, monkeypatch):
    monkeypatch.setattr(storage, "MAX_UPLOAD_MB", 0)
    response = client.post(
        "/datasets/upload",
        files={"file": ("big.csv", CSV_CONTENT, "text/csv")},
    )
    assert response.status_code == 400


def test_post_and_get_checks(client: TestClient):
    dataset = upload(client)
    checks = [
        {"column": "id", "check_type": "not_null"},
        {"column": "age", "check_type": "mean_within_pct", "params": {"pct": 0.1}},
    ]

    response = client.post(f"/datasets/{dataset['id']}/checks", json=checks)
    assert response.status_code == 200, response.text
    saved = response.json()
    assert len(saved) == 2
    assert all(c["active"] for c in saved)

    response = client.get(f"/datasets/{dataset['id']}/checks")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_post_checks_replaces_previously_active_set(client: TestClient):
    dataset = upload(client)
    client.post(f"/datasets/{dataset['id']}/checks", json=[{"column": "id", "check_type": "not_null"}])
    client.post(f"/datasets/{dataset['id']}/checks", json=[{"column": "age", "check_type": "not_null"}])

    response = client.get(f"/datasets/{dataset['id']}/checks")
    active = response.json()
    assert len(active) == 1
    assert active[0]["column"] == "age"


def test_run_checks_drops_drift_check_on_first_run_then_fires_on_second(client: TestClient):
    dataset = upload(client)
    checks = [
        {"column": "id", "check_type": "not_null"},
        {"column": "age", "check_type": "mean_within_pct", "params": {"pct": 0.1}},
    ]
    client.post(f"/datasets/{dataset['id']}/checks", json=checks)

    run1 = client.post(f"/datasets/{dataset['id']}/run-checks")
    assert run1.status_code == 200, run1.text
    results1 = run1.json()["results"]
    assert len(results1) == 1
    assert results1[0]["check_type"] == "not_null"

    run2 = client.post(f"/datasets/{dataset['id']}/run-checks")
    assert run2.status_code == 200
    results2 = run2.json()["results"]
    assert len(results2) == 2
    mean_result = next(r for r in results2 if r["check_type"] == "mean_within_pct")
    assert mean_result["passed"] is True


def test_history_returns_runs_in_order(client: TestClient):
    dataset = upload(client)
    client.post(f"/datasets/{dataset['id']}/checks", json=[{"column": "id", "check_type": "not_null"}])
    client.post(f"/datasets/{dataset['id']}/run-checks")
    client.post(f"/datasets/{dataset['id']}/run-checks")

    response = client.get(f"/datasets/{dataset['id']}/history")
    assert response.status_code == 200
    history = response.json()
    assert len(history) == 2
    assert history[0]["run_at"] <= history[1]["run_at"]
    assert history[0]["results"][0]["check_type"] == "not_null"


def test_suggest_checks_returns_agent_output(client: TestClient, monkeypatch):
    dataset = upload(client)
    from checkyourdata.schema import CheckConfig, CheckSource, CheckType

    stub_checks = [CheckConfig(column="id", check_type=CheckType.NOT_NULL, source=CheckSource.AI_SUGGESTED)]
    monkeypatch.setattr("checkyourdata.api.routes.agent_suggest_checks", lambda *a, **kw: stub_checks)

    response = client.post(f"/datasets/{dataset['id']}/suggest-checks")
    assert response.status_code == 200, response.text
    body = response.json()
    assert len(body) == 1
    assert body[0]["check_type"] == "not_null"
    assert body[0]["source"] == "ai_suggested"


def test_suggest_checks_uses_cache_on_second_call(client: TestClient, monkeypatch):
    dataset = upload(client)
    from checkyourdata.schema import CheckConfig, CheckSource, CheckType

    stub_checks = [CheckConfig(column="id", check_type=CheckType.NOT_NULL, source=CheckSource.AI_SUGGESTED)]
    call_count = {"n": 0}

    def fake_agent(*args, **kwargs):
        call_count["n"] += 1
        return stub_checks

    monkeypatch.setattr("checkyourdata.api.routes.agent_suggest_checks", fake_agent)

    client.post(f"/datasets/{dataset['id']}/suggest-checks")
    client.post(f"/datasets/{dataset['id']}/suggest-checks")

    assert call_count["n"] == 1


def test_suggest_checks_surfaces_agent_failure_as_502(client: TestClient, monkeypatch):
    dataset = upload(client)
    from checkyourdata.agent import AgentSuggestionError

    def fake_agent(*args, **kwargs):
        raise AgentSuggestionError("model never produced valid output")

    monkeypatch.setattr("checkyourdata.api.routes.agent_suggest_checks", fake_agent)

    response = client.post(f"/datasets/{dataset['id']}/suggest-checks")
    assert response.status_code == 502
    assert "model never produced valid output" in response.json()["detail"]


@pytest.mark.parametrize(
    "method,path",
    [
        ("get", "/datasets/999"),
        ("get", "/datasets/999/schema"),
        ("get", "/datasets/999/checks"),
        ("post", "/datasets/999/checks"),
        ("post", "/datasets/999/run-checks"),
        ("get", "/datasets/999/history"),
        ("post", "/datasets/999/suggest-checks"),
    ],
)
def test_unknown_dataset_returns_404(client: TestClient, method: str, path: str):
    kwargs = {"json": []} if method == "post" and path.endswith("/checks") else {}
    response = getattr(client, method)(path, **kwargs)
    assert response.status_code == 404
