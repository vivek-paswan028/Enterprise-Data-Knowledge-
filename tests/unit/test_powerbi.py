from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_powerbi_dashboard_ui_endpoint():
    response = client.get("/powerbi/dashboard")
    assert response.status_code == 200
    assert "Power BI Executive Dashboard 2026" in response.text


def test_powerbi_dataset_endpoint():
    response = client.get("/powerbi/datasets/fact_sales")
    assert response.status_code == 200
    json_data = response.json()
    assert "kpis" in json_data
    assert "total_gross_revenue" in json_data["kpis"]
    assert "record_count" in json_data


def test_powerbi_csv_download():
    response = client.get("/powerbi/datasets/download/csv?table=fact_sales")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
