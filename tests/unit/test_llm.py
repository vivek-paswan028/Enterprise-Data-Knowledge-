import pytest
from fastapi.testclient import TestClient
from src.api.main import app
from src.llm.validator import SQLSecurityValidator
from src.llm.engine import TextToSQLEngine

client = TestClient(app)


def test_sql_security_validator_blocks_destructive_queries():
    # 1. Valid SELECT query
    valid = SQLSecurityValidator.validate_sql("SELECT * FROM fact_sales WHERE status = 'COMPLETED';")
    assert valid.is_safe is True
    assert len(valid.violations) == 0

    # 2. Block DROP TABLE
    drop_test = SQLSecurityValidator.validate_sql("DROP TABLE dim_customers;")
    assert drop_test.is_safe is False
    assert any("DROP" in v for v in drop_test.violations)

    # 3. Block DELETE statement
    delete_test = SQLSecurityValidator.validate_sql("DELETE FROM fact_sales WHERE sales_key = 10;")
    assert delete_test.is_safe is False

    # 4. Block Comment injection attack
    comment_test = SQLSecurityValidator.validate_sql("SELECT * FROM dim_customers; -- drop table")
    assert comment_test.is_safe is False


def test_text_to_sql_engine_execution():
    engine = TextToSQLEngine()
    response = engine.process_query("Show total revenue by status")

    assert response.is_safe is True
    assert "SELECT" in response.generated_sql
    assert response.row_count > 0
    assert "status" in response.columns
    assert "total_revenue" in response.columns


def test_llm_query_rest_api_endpoint():
    # 1. Authenticate to get JWT token
    login_resp = client.post("/api/v1/auth/token", data={"username": "admin", "password": "admin123"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Query endpoint
    query_payload = {"natural_language_query": "What is the total revenue by city?"}
    response = client.post("/api/v1/llm/query", json=query_payload, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["is_safe"] is True
    assert len(data["rows"]) > 0
    assert "city" in data["columns"]
