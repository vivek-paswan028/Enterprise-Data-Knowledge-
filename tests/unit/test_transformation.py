import pytest
from pathlib import Path
import polars as pl
from src.transformation.schemas import MedallionLayer
from src.transformation.medallion import MedallionTransformer


@pytest.fixture
def sample_raw_parquet(tmp_path: Path) -> Path:
    raw_path = tmp_path / "orders_raw.parquet"
    df = pl.DataFrame({
        "Order ID": [101, 102, 102, 103],  # Duplicate 102
        "Customer ID": [" C1 ", " C2 ", " C2 ", " C3 "],  # Trailing/leading whitespace
        "Amount": [250.0, 100.0, 100.0, 450.0],
        "Status": ["COMPLETED", "PENDING", "PENDING", "COMPLETED"]
    })
    df.write_parquet(raw_path)
    return raw_path


def test_medallion_pipeline_execution(sample_raw_parquet: Path, tmp_path: Path):
    transformer = MedallionTransformer(base_dir=tmp_path / "processed")

    # 1. Bronze Layer execution
    bronze_summary = transformer.process_bronze("orders", sample_raw_parquet)
    assert bronze_summary.layer == MedallionLayer.BRONZE
    assert bronze_summary.input_records == 4
    df_bronze = pl.read_parquet(bronze_summary.output_file_path)
    assert "_raw_source_file" in df_bronze.columns
    assert "_ingested_at" in df_bronze.columns

    # 2. Silver Layer execution (deduplication & standardization)
    silver_summary = transformer.process_silver(
        "orders",
        Path(bronze_summary.output_file_path),
        primary_keys=["Order ID"]
    )
    assert silver_summary.layer == MedallionLayer.SILVER
    assert silver_summary.input_records == 4
    assert silver_summary.output_records == 3  # 1 duplicate dropped
    assert silver_summary.dropped_duplicates == 1

    df_silver = pl.read_parquet(silver_summary.output_file_path)
    assert df_silver.columns == ["order_id", "customer_id", "amount", "status", "_raw_source_file", "_ingested_at"]
    # Check whitespace trimmed
    assert df_silver["customer_id"].to_list() == ["C1", "C2", "C3"]

    # 3. Gold Layer execution (Analytical Aggregation)
    gold_summary = transformer.process_gold("orders", Path(silver_summary.output_file_path))
    assert gold_summary.layer == MedallionLayer.GOLD
    df_gold = pl.read_parquet(gold_summary.output_file_path)
    assert "status" in df_gold.columns
    assert "total_revenue" in df_gold.columns
    assert len(df_gold) == 2  # COMPLETED and PENDING statuses
