# Enterprise Power BI Integration Blueprint

This guide provides the complete architectural setup for connecting **Power BI Desktop & Power BI Service** to the **DataPulse AI PostgreSQL Data Warehouse**.

---

## 1. Data Connection Architecture

Power BI connects directly to the PostgreSQL 16 Data Warehouse populated by our Medallion Gold aggregated datasets.

```
┌─────────────────────────────────────────────────────────────┐
│  DataPulse PostgreSQL 16 Data Warehouse                     │
│  (Database: datapulse_warehouse | Port: 5432)               │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼ PostgreSQL Native Connector
┌─────────────────────────────────────────────────────────────┐
│  Power BI Data Model (Star Schema)                          │
│  ┌───────────────────┐      ┌────────────────────┐          │
│  │   dim_customers   │ 1  * │     fact_sales     │          │
│  │ ───────────────── │◄────┤ ────────────────── │          │
│  │ PK customer_key   │      │ FK customer_key    │          │
│  └───────────────────┘      │ FK product_key ────┤*         │
│                             └────────────────────┘│         │
│                                                   │ 1       │
│                             ┌────────────────────┐│         │
│                             │   dim_products     ││         │
│                             │ ────────────────── │◄┘        │
│                             │ PK product_key     │          │
│                             └────────────────────┘          │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Executive Business KPI Dashboard                           │
│  - Total Revenue & Order Volumes                            │
│  - Regional Revenue Heatmaps (by City)                      │
│  - Order Status Funnel (Completed vs Cancelled)             │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Connectivity Mode Strategy (Import vs DirectQuery)

| Mode | Recommendation | Best Used For |
| :--- | :--- | :--- |
| **Import Mode** | **Recommended for Gold Aggregations** | Loads aggregated Gold datasets into Power BI VertiPaq in-memory engine. Provides ultra-fast interactive report visuals. |
| **DirectQuery** | Recommended for Real-Time Operational Monitoring | Issues live SQL queries against PostgreSQL `fact_sales` on every dashboard slicer interaction. Use when real-time sub-second latency is required. |

---

## 3. DAX Business KPI Measures

Copy and paste the following DAX measures directly into your Power BI Data Model:

### 1. Total Gross Revenue
```dax
Total Revenue = SUM(fact_sales[amount])
```

### 2. Completed Orders Revenue
```dax
Completed Revenue = 
CALCULATE(
    SUM(fact_sales[amount]),
    fact_sales[status] = "COMPLETED"
)
```

### 3. Average Order Value (AOV)
```dax
Average Order Value = 
DIVIDE(
    [Total Revenue], 
    COUNT(fact_sales[sales_key]), 
    0
)
```

### 4. Cancellation Rate (%)
```dax
Cancellation Rate = 
DIVIDE(
    CALCULATE(COUNT(fact_sales[sales_key]), fact_sales[status] = "CANCELLED"),
    COUNT(fact_sales[sales_key]),
    0
) * 100
```

---

## 4. Connecting Power BI Desktop (Step-by-Step)

1. Open **Power BI Desktop** -> Click **Get Data** -> Select **PostgreSQL database**.
2. Enter Server Details:
   - **Server**: `localhost:5432` (or container IP in production)
   - **Database**: `datapulse_warehouse`
   - **Data Connectivity mode**: Select `Import` or `DirectQuery`.
3. Enter Credentials:
   - **User**: `datapulse_user`
   - **Password**: `datapulse_password`
4. In the Navigator pane, select `dim_customers`, `dim_products`, `fact_sales`, and `fact_ingestion_audit`.
5. Verify Relationship Cardinality:
   - `dim_customers[customer_key]` `1` ---> `*` `fact_sales[customer_key]` (Single Direction Filter).
