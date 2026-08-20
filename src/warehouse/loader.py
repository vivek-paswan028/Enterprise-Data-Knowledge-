from pathlib import Path
from typing import Optional, Dict, Any
import polars as pl
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import Session
from src.utils.logger import export_logger as logger
from src.warehouse.connection import get_sync_engine
from src.warehouse.models import DimCustomer, DimProduct, FactSales, FactIngestionAudit


class WarehouseLoader:
    """
    Enterprise Data Warehouse Bulk Loader.
    Loads Silver/Gold Parquet datasets into PostgreSQL/SQLite relational tables
    with primary key deduplication and foreign key dimension lookup resolution.
    """

    def __init__(self, session: Optional[Session] = None):
        self.session = session

    def _get_session(self) -> Session:
        if self.session:
            return self.session
        return Session(get_sync_engine())

    def load_customers(self, silver_parquet_path: Path) -> int:
        df = pl.read_parquet(silver_parquet_path)
        session = self._get_session()

        loaded_count = 0
        try:
            for row in df.iter_rows(named=True):
                cust_id = str(row.get("customer_id", "")).strip()
                if not cust_id:
                    continue

                # Upsert check
                existing = session.scalar(
                    select(DimCustomer).where(DimCustomer.customer_id == cust_id)
                )
                if not existing:
                    customer = DimCustomer(
                        customer_id=cust_id,
                        name=row.get("name", f"Customer_{cust_id}"),
                        email=row.get("email"),
                        city=row.get("city")
                    )
                    session.add(customer)
                    loaded_count += 1
                else:
                    # Update fields if changed
                    if "city" in row and row["city"]:
                        existing.city = row["city"]

            session.commit()
            logger.info(f"Loaded/Updated {loaded_count} customer records into dim_customers")
            return loaded_count
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to load dim_customers: {str(e)}")
            raise e

    def load_sales_facts(self, silver_parquet_path: Path) -> int:
        df = pl.read_parquet(silver_parquet_path)
        session = self._get_session()

        loaded_count = 0
        try:
            for row in df.iter_rows(named=True):
                order_id = str(row.get("order_id", ""))
                cust_id = str(row.get("customer_id", "")).strip()
                amount = float(row.get("amount", 0.0))
                status = str(row.get("status", "COMPLETED")).strip()

                # Resolve customer dimension key
                customer = session.scalar(
                    select(DimCustomer).where(DimCustomer.customer_id == cust_id)
                )
                if not customer:
                    # Auto-create fallback customer record
                    customer = DimCustomer(customer_id=cust_id, name=f"Customer_{cust_id}")
                    session.add(customer)
                    session.flush()

                fact = FactSales(
                    order_id=order_id,
                    customer_key=customer.customer_key,
                    amount=amount,
                    status=status
                )
                session.add(fact)
                loaded_count += 1

            session.commit()
            logger.info(f"Loaded {loaded_count} sales fact records into fact_sales")
            return loaded_count
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to load fact_sales: {str(e)}")
            raise e

    def record_audit(
        self,
        dataset_name: str,
        record_count: int,
        quality_score: float,
        drift_type: str,
        raw_file_name: str,
        is_quarantined: bool = False
    ) -> FactIngestionAudit:
        session = self._get_session()
        audit = FactIngestionAudit(
            dataset_name=dataset_name,
            record_count=record_count,
            quality_score=quality_score,
            drift_type=drift_type,
            raw_file_name=raw_file_name,
            is_quarantined=is_quarantined
        )
        session.add(audit)
        session.commit()
        return audit
