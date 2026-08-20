import pytest
from pathlib import Path
import polars as pl
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from src.warehouse.connection import Base
from src.warehouse.models import DimCustomer, FactSales, FactIngestionAudit
from src.warehouse.loader import WarehouseLoader


@pytest.fixture
def in_memory_db_session() -> Session:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = Session(engine)
    yield session
    session.close()


@pytest.fixture
def sample_silver_parquet(tmp_path: Path) -> Path:
    silver_path = tmp_path / "orders_silver.parquet"
    df = pl.DataFrame({
        "order_id": ["101", "102"],
        "customer_id": ["C1001", "C1002"],
        "name": ["Alice", "Bob"],
        "email": ["alice@test.com", "bob@test.com"],
        "city": ["Seattle", "New York"],
        "amount": [250.50, 100.00],
        "status": ["COMPLETED", "PENDING"]
    })
    df.write_parquet(silver_path)
    return silver_path


def test_warehouse_loader_customers_and_sales(
    sample_silver_parquet: Path,
    in_memory_db_session: Session
):
    loader = WarehouseLoader(session=in_memory_db_session)

    # 1. Load customers dimension
    cust_count = loader.load_customers(sample_silver_parquet)
    assert cust_count == 2

    customers = in_memory_db_session.scalars(select(DimCustomer)).all()
    assert len(customers) == 2
    assert customers[0].customer_id == "C1001"
    assert customers[0].city == "Seattle"

    # 2. Load sales facts
    sales_count = loader.load_sales_facts(sample_silver_parquet)
    assert sales_count == 2

    sales = in_memory_db_session.scalars(select(FactSales)).all()
    assert len(sales) == 2
    assert sales[0].order_id == "101"
    assert sales[0].amount == 250.50
    assert sales[0].customer.customer_id == "C1001"


def test_record_audit_log(in_memory_db_session: Session):
    loader = WarehouseLoader(session=in_memory_db_session)
    audit = loader.record_audit(
        dataset_name="orders_test",
        record_count=100,
        quality_score=98.5,
        drift_type="no_drift",
        raw_file_name="orders_2026.csv",
        is_quarantined=False
    )

    assert audit.audit_id is not None
    assert audit.dataset_name == "orders_test"
    assert audit.quality_score == 98.5
