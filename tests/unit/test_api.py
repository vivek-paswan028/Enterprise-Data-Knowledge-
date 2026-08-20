import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_health_check_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert "project" in data


def test_authentication_flow():
    # 1. Invalid login
    bad_resp = client.post(
        "/api/v1/auth/token",
        data={"username": "admin", "password": "wrong_password"}
    )
    assert bad_resp.status_code == 401

    # 2. Valid login
    good_resp = client.post(
        "/api/v1/auth/token",
        data={"username": "admin", "password": "admin123"}
    )
    assert good_resp.status_code == 200
    token_data = good_resp.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    return token_data["access_token"]


def test_file_upload_and_pipeline_execution(tmp_path: Path):
    token = test_authentication_flow()
    headers = {"Authorization": f"Bearer {token}"}

    # Create dummy CSV file
    csv_content = "order_id,customer_id,amount,status\n201,C500,350.00,COMPLETED\n202,C501,120.00,PENDING\n"
    files = {"file": ("test_orders.csv", csv_content, "text/csv")}

    # Upload endpoint check
    upload_resp = client.post("/api/v1/data/upload", headers=headers, files=files)
    assert upload_resp.status_code == 200
    upload_data = upload_resp.json()
    assert len(upload_data) == 1
    assert upload_data[0]["record_count"] == 2
    assert upload_data[0]["quality_score"] == 100.0

    # Pipeline execution endpoint check
    pipe_resp = client.post("/api/v1/pipeline/run", headers=headers)
    assert pipe_resp.status_code == 200
    pipe_data = pipe_resp.json()
    assert pipe_data["status"] == "SUCCESS"

    # KPI Summary endpoint check
    kpi_resp = client.get("/api/v1/kpi/summary", headers=headers)
    assert kpi_resp.status_code == 200
    kpi_data = kpi_resp.json()
    assert kpi_data["total_records"] > 0
    assert kpi_data["total_revenue"] > 0.0
