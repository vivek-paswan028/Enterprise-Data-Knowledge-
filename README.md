# Enterprise Data Intelligence Platform 2026

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Pandas](https://img.shields.io/badge/Pandas-2.0+-150458.svg)
![NumPy](https://img.shields.io/badge/NumPy-1.24+-013243.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791.svg)
![SQL](https://img.shields.io/badge/SQL-Analytical-orange.svg)
![Power BI](https://img.shields.io/badge/Power_BI-Visualizations-F2C811.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)
![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED.svg)

---

## 📌 Executive Summary

**Enterprise Data Intelligence Platform 2026** is an end-to-end data processing, analytics, and business intelligence platform. It automates multi-source data ingestion, schema drift detection, data quality validation, Medallion ETL transformations (Bronze ➔ Silver ➔ Gold), and structured loading into a relational PostgreSQL Data Warehouse. Interactive Power BI dashboards and executive KPIs leverage this warehouse to drive actionable, data-driven decisions across the enterprise.

---

## 🎯 Business Problems Solved

Modern enterprises struggle with fragmented data, inconsistent metrics, and poor data quality. This platform addresses critical enterprise data challenges:

1. **Elimination of Data Silos & Fragmented Sources**
   - *Problem*: Enterprise sales, customer, and product data are often trapped across disparate CSV files, external APIs, and legacy databases.
   - *Solution*: Provides an automated, unified ingestion engine supporting multi-format files and API integration into a central PostgreSQL Data Warehouse.

2. **Mitigation of Data Quality Decay & Schema Drift**
   - *Problem*: Unexpected upstream schema modifications or invalid data entries break downstream analytics and create reporting errors.
   - *Solution*: Implements automated schema drift detection, strict Pydantic/Python type validation, and an automated quarantine isolation pipeline for corrupt records.

3. **High Latency & Manual ETL Processing Overhead**
   - *Problem*: Manual spreadsheet manipulations and unoptimized ETL pipelines delay business reporting cycles by days or weeks.
   - *Solution*: Leverages vectorized Pandas and NumPy processing within a Medallion Architecture (Bronze ➔ Silver ➔ Gold) for fast automated data cleaning, deduplication, and aggregation.

4. **Lack of Real-Time Executive Visibility & Delayed Decision-Making**
   - *Problem*: Stakeholders lack immediate visibility into critical business KPIs such as net revenue, order completion rates, and regional demand shifts.
   - *Solution*: Delivers an interactive Power BI Executive Dashboard featuring real-time DAX metrics, interactive slicers, and regional heatmaps for instant executive insights.

5. **Revenue Leakage & Order Cancellation Tracking**
   - *Problem*: Unidentified bottlenecks in sales funnels lead to high cancellation rates and missed revenue targets.
   - *Solution*: Calculates live DAX metrics (*Cancellation Rate %*, *Average Order Value*, *Realized Gross Revenue*) to pinpoint operational inefficiencies across regions and product categories.

---

## 🛠 Tech Stack

- **Core Programming**: Python 3.11+
- **Data Manipulation & Workflows**: Pandas, NumPy
- **Data Warehouse & Database**: PostgreSQL 16, SQL (Analytical & Dimensional Modeling), SQLAlchemy, Alembic
- **Analytics & Visualization**: Power BI (Import & DirectQuery, DAX Modeling, Star Schema), Chart.js
- **API & Pipeline Services**: FastAPI, Pydantic v2, Apache Airflow / Orchestration
- **Infrastructure & Containerization**: Docker, Docker Compose, PyTest

---

## Key Highlights & Achievements

- **End-to-End Enterprise Data Pipeline**: Engineered an automated data pipeline using Python and SQL for multi-source data ingestion, strict schema validation, Medallion transformation, and analytical data loading.
- **Modular ETL Workflows**: Developed modular ETL pipelines with Python, Pandas, and NumPy to clean, standardize, validate, and integrate structured and semi-structured datasets.
- **PostgreSQL Data Warehouse Design**: Designed a star-schema relational PostgreSQL data warehouse with optimized indexing and analytical SQL queries to produce business-ready datasets and actionable insights.
- **Interactive Power BI Dashboards**: Built interactive Power BI dashboards (utilizing DAX measures and dimensional models) to visualize critical business metrics, sales funnels, and executive KPIs for stakeholders.

---

## 🏗 System Architecture

```
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                                 1. Multi-Source Ingestion                                │
│   - Multi-format ingestion (CSV, Parquet, JSON APIs)                                     │
│   - Automatic Schema Drift Detection & Type Enforcement                                  │
└──────────────────────────────────────────┬───────────────────────────────────────────────┘
                                           │
                                           ▼
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                               2. Validation & Quarantine                                 │
│   - Strict validation rules (Null check, Range constraints, Foreign keys)                 │
│   - Automated quarantine pipeline for invalid record isolation                           │
└──────────────────────────────────────────┬───────────────────────────────────────────────┘
                                           │
                                           ▼
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                             3. Medallion ETL Transformation                              │
│   - Bronze Layer: Raw ingestion & audit metadata                                         │
│   - Silver Layer: Deduplication, cleansing, schema normalization (Pandas & NumPy)        │
│   - Gold Layer: Business aggregations, dimensional modeling, KPI metrics                │
└──────────────────────────────────────────┬───────────────────────────────────────────────┘
                                           │
                                           ▼
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                          4. PostgreSQL Data Warehouse & SQL                              │
│   - Relational Star Schema (dim_customers, dim_products, fact_sales)                     │
│   - Analytical SQL queries & materialized views for fast analytical access               │
└──────────────────────────────────────────┬───────────────────────────────────────────────┘
                                           │
                                           ▼
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                              5. Power BI Analytics & REST APIs                           │
│   - Power BI Executive Dashboard & Web UI (DAX KPI calculations, interactive slicers)    │
│   - FastAPI REST Endpoints for live dataset streaming & pipeline orchestration           │
└──────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 Power BI Analytics & Executive Dashboard

This platform includes a complete **Power BI Analytics Suite** equipped with an interactive web dashboard, dummy dataset generator, REST API connectors, and DAX business measures.

### 1. Interactive Power BI Web Dashboard
Access the embedded live Power BI Dashboard at `http://localhost:8000/powerbi/dashboard` when running the application.

- **Executive KPI Cards**: Real-time calculated *Total Gross Revenue ($)*, *Completed Revenue ($)*, *Total Orders*, *Average Order Value (AOV)*, and *Cancellation Rate (%)*.
- **Dynamic Slicers**: Interactive filtering by *Time Period (Q1, Q2, Q3 2026)*, *Product Category*, *Region / City*, and *Order Status*.
- **Executive Visuals**:
  - *Monthly Revenue & Order Volume Trend* (Dual-axis Line & Bar Chart)
  - *Revenue by Product Category* (Donut Chart)
  - *Regional Revenue Heatmap* (Horizontal Bar Chart across 10 top global cities)
  - *Order Status Distribution Funnel* (Pie Chart)
- **Data Table & DAX Explorer**: Live searchable table of Gold warehouse records and an interactive DAX measures modal.

### 2. Dummy Enterprise Dataset Generator
Run `python3 scripts/generate_dummy_data.py` to generate realistic dummy datasets formatted for direct import into Power BI Desktop:
- `data/raw/dim_customers.csv` (50 Enterprise Clients)
- `data/raw/dim_products.csv` (15 Products across 5 Categories)
- `data/raw/fact_sales.csv` (600+ Sales Transaction Records)

### 3. Key DAX KPI Measures
```dax
// 1. Total Gross Revenue
Total Revenue = SUM(fact_sales[amount])

// 2. Completed Revenue
Completed Revenue = 
CALCULATE(
    SUM(fact_sales[amount]),
    fact_sales[status] = "COMPLETED"
)

// 3. Average Order Value (AOV)
Average Order Value = 
DIVIDE([Total Revenue], COUNT(fact_sales[sales_key]), 0)

// 4. Cancellation Rate (%)
Cancellation Rate = 
DIVIDE(
    CALCULATE(COUNT(fact_sales[sales_key]), fact_sales[status] = "CANCELLED"),
    COUNT(fact_sales[sales_key]),
    0
) * 100
```

For detailed guidance on connecting **Power BI Desktop & Power BI Service** to the PostgreSQL Data Warehouse, configuring DirectQuery vs Import mode, and setting up star schemas, see the [Power BI Integration Guide](docs/powerbi_integration_guide.md).

---

## 📁 Repository Structure

```
.
├── .github/workflows/      # Automated CI/CD workflows
├── dags/                   # Apache Airflow DAGs for pipeline orchestration
├── dashboard/              # Interactive Power BI Executive Dashboard Web App
│   └── index.html
├── data/                   # Data directories (raw, processed, quarantine)
├── docs/                   # System documentation & Power BI integration guides
│   └── powerbi_integration_guide.md
├── scripts/                # Utility scripts & dummy data generator
│   └── generate_dummy_data.py
├── src/                    # Primary application source code
│   ├── api/                # FastAPI application, routers (including Power BI router) & security
│   ├── config/             # Environment configurations & settings
│   ├── ingestion/          # Ingestion engines, parsers & drift detectors
│   ├── llm/                # Intelligent prompt & schema validation utilities
│   ├── transformation/     # Medallion ETL transformations (Pandas/NumPy)
│   ├── utils/              # Logging, helpers & system utilities
│   ├── validation/         # Quality validation & quarantine engine
│   └── warehouse/          # PostgreSQL database models, loaders & connection pools
├── tests/                  # Comprehensive unit & integration PyTest suite
├── Dockerfile              # Containerization image build configuration
├── docker-compose.yml      # Multi-container service definitions (App, PostgreSQL)
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
```

---

## 🚀 Getting Started

### Prerequisites

- **Python**: 3.11 or higher
- **PostgreSQL**: 16+ (or run via Docker Compose)
- **Docker & Docker Compose**: Recommended for local deployment
- **Power BI Desktop**: Optional, for viewing and editing `.pbix` reports

---

### Setup & Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/vivek-paswan028/Enterprise-Data-Knowledge-.git
   cd Enterprise-Data-Knowledge-
   ```

2. **Set Up Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Generate Dummy Enterprise Data**
   ```bash
   python3 scripts/generate_dummy_data.py
   ```

4. **Configure Environment Variables**
   ```bash
   cp .env.example .env
   # Edit .env with your PostgreSQL credentials and database configurations
   ```

5. **Launch Infrastructure via Docker Compose**
   ```bash
   docker-compose up -d --build
   ```

6. **Run FastAPI Server & Power BI Dashboard**
   ```bash
   uvicorn src.api.main:app --reload --port 8000
   ```
   - **Power BI Executive Dashboard**: `http://localhost:8000/powerbi/dashboard`
   - **Interactive API Documentation**: `http://localhost:8000/docs`

---

## 🧪 Testing & Quality Assurance

Run the comprehensive unit and integration test suite using `pytest`:

```bash
pytest -v --tb=short
```

---

## 📄 License

This project is released under the MIT License.
