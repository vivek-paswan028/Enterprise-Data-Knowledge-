from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.warehouse.connection import Base


class DimCustomer(Base):
    __tablename__ = "dim_customers"

    customer_key: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_id: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    sales: Mapped[list["FactSales"]] = relationship("FactSales", back_populates="customer")


class DimProduct(Base):
    __tablename__ = "dim_products"

    product_key: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    sales: Mapped[list["FactSales"]] = relationship("FactSales", back_populates="product")


class FactSales(Base):
    __tablename__ = "fact_sales"

    sales_key: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    customer_key: Mapped[int] = mapped_column(Integer, ForeignKey("dim_customers.customer_key"), nullable=False)
    product_key: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("dim_products.product_key"), nullable=True)
    
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    order_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    customer: Mapped["DimCustomer"] = relationship("DimCustomer", back_populates="sales")
    product: Mapped[Optional["DimProduct"]] = relationship("DimProduct", back_populates="sales")


class FactIngestionAudit(Base):
    __tablename__ = "fact_ingestion_audit"

    audit_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dataset_name: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    record_count: Mapped[int] = mapped_column(Integer, nullable=False)
    quality_score: Mapped[float] = mapped_column(Float, nullable=False)
    drift_type: Mapped[str] = mapped_column(String(50), nullable=False)
    is_quarantined: Mapped[bool] = mapped_column(Boolean, default=False)
    raw_file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
