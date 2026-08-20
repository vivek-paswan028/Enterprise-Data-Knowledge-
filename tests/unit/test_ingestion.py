import pytest
import json
from pathlib import Path
import polars as pl
from src.ingestion.schemas import SupportedFormat, DriftType
from src.ingestion.parsers import MultiFormatParser
from src.ingestion.drift_detector import (
    SchemaFingerprinter,
    SchemaDriftDetector,
    MetadataRegistry
)
from src.ingestion.manager import IngestionManager


@pytest.fixture
def sample_csv(tmp_path: Path) -> Path:
    csv_path = tmp_path / "orders.csv"
    content = "order_id,customer_id,amount,status\n101,C1,250.50,COMPLETED\n102,C2,100.00,PENDING\n"
    csv_path.write_text(content, encoding="utf-8")
    return csv_path


@pytest.fixture
def sample_json(tmp_path: Path) -> Path:
    json_path = tmp_path / "customers.json"
    data = [
        {"customer_id": "C1", "name": "Alice", "city": "New York"},
        {"customer_id": "C2", "name": "Bob", "city": "Seattle"}
    ]
    json_path.write_text(json.dumps(data), encoding="utf-8")
    return json_path


@pytest.fixture
def sample_sql_dump(tmp_path: Path) -> Path:
    sql_path = tmp_path / "dump.sql"
    content = """
    INSERT INTO `products` (`product_id`, `name`, `price`) VALUES
    (1, 'Laptop', 1200.00),
    (2, 'Mouse', 25.50);
    """
    sql_path.write_text(content, encoding="utf-8")
    return sql_path


def test_parse_csv(sample_csv: Path):
    result = MultiFormatParser.parse_file(sample_csv, SupportedFormat.CSV)
    assert "default" in result
    df = result["default"]
    assert len(df) == 2
    assert df.columns == ["order_id", "customer_id", "amount", "status"]


def test_parse_json(sample_json: Path):
    result = MultiFormatParser.parse_file(sample_json, SupportedFormat.JSON)
    assert "default" in result
    df = result["default"]
    assert len(df) == 2
    assert "name" in df.columns


def test_parse_sql_dump(sample_sql_dump: Path):
    result = MultiFormatParser.parse_file(sample_sql_dump, SupportedFormat.SQL_DUMP)
    df = result["default"]
    assert len(df) == 2
    assert df.columns == ["product_id", "name", "price"]


def test_schema_fingerprint_and_drift_detection(tmp_path: Path):
    df_v1 = pl.DataFrame({
        "user_id": [1, 2],
        "email": ["a@test.com", "b@test.com"]
    })

    df_v2_new_col = pl.DataFrame({
        "user_id": [1, 2],
        "email": ["a@test.com", "b@test.com"],
        "age": [25, 30]
    })

    fp1 = SchemaFingerprinter.compute_fingerprint("users", df_v1)
    fp2 = SchemaFingerprinter.compute_fingerprint("users", df_v2_new_col)

    registry_path = tmp_path / "metadata_registry.json"
    registry = MetadataRegistry(registry_path)

    # Initial evaluation
    report1 = SchemaDriftDetector.evaluate_drift(fp1, registry.get_registered_schema("users"))
    assert report1.drift_type == DriftType.NO_DRIFT
    registry.register_schema(fp1)

    # Secondary evaluation with added column
    report2 = SchemaDriftDetector.evaluate_drift(fp2, registry.get_registered_schema("users"))
    assert report2.drift_type == DriftType.NEW_COLUMNS
    assert report2.is_breaking is False
    assert "age" in report2.added_columns


def test_ingestion_manager(sample_csv: Path, tmp_path: Path):
    manager = IngestionManager(registry_path=tmp_path / "metadata.json")
    payloads = manager.process_file(sample_csv, SupportedFormat.CSV, dataset_name="orders_test")

    assert len(payloads) == 1
    p = payloads[0]
    assert p.record_count == 2
    assert Path(p.staged_parquet_path).exists()
