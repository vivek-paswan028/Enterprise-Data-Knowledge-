import os
import pandas as pd
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from typing import Optional, List

router = APIRouter(prefix="/powerbi", tags=["Power BI Intelligence Dashboard"])


@router.get("/dashboard", response_class=HTMLResponse)
async def get_powerbi_dashboard():
    """Serves the interactive Power BI Executive Dashboard 2026 UI."""
    dashboard_path = os.path.join(os.getcwd(), "dashboard", "index.html")
    if not os.path.exists(dashboard_path):
        raise HTTPException(status_code=404, detail="Dashboard UI file not found")
    with open(dashboard_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@router.get("/datasets/fact_sales")
async def get_fact_sales_dataset(
    category: Optional[str] = Query(None, description="Filter by Product Category"),
    status: Optional[str] = Query(None, description="Filter by Order Status"),
    city: Optional[str] = Query(None, description="Filter by Region / City")
):
    """Provides Gold Fact Sales dataset for Power BI REST / Web connector."""
    csv_path = os.path.join(os.getcwd(), "data", "raw", "fact_sales.csv")
    if not os.path.exists(csv_path):
        raise HTTPException(status_code=404, detail="fact_sales.csv dataset not found")
    
    df = pd.read_csv(csv_path)
    
    if category and category != "ALL":
        df = df[df["category"] == category]
    if status and status != "ALL":
        df = df[df["status"] == status]
    if city and city != "ALL":
        df = df[df["city"] == city]
        
    records = df.to_dict(orient="records")
    
    # Calculate DAX KPIs dynamically
    total_revenue = float(df["amount"].sum()) if not df.empty else 0.0
    completed_revenue = float(df[df["status"] == "COMPLETED"]["amount"].sum()) if not df.empty else 0.0
    total_orders = len(df)
    aov = total_revenue / total_orders if total_orders > 0 else 0.0
    cancelled_count = len(df[df["status"] == "CANCELLED"])
    cancel_rate = (cancelled_count / total_orders * 100.0) if total_orders > 0 else 0.0
    
    return {
        "kpis": {
            "total_gross_revenue": total_revenue,
            "completed_revenue": completed_revenue,
            "total_orders": total_orders,
            "average_order_value": aov,
            "cancellation_rate_pct": round(cancel_rate, 2)
        },
        "record_count": total_orders,
        "data": records
    }


@router.get("/datasets/download/csv")
async def download_powerbi_csv(table: str = Query("fact_sales", enum=["fact_sales", "dim_customers", "dim_products"])):
    """Allows downloading formatted CSV datasets directly for Power BI Desktop Import Mode."""
    file_name = f"{table}.csv"
    file_path = os.path.join(os.getcwd(), "data", "raw", file_name)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Dataset {file_name} not found")
    return FileResponse(path=file_path, filename=file_name, media_type="text/csv")
