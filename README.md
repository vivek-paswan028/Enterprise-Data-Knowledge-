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

## 🛠 Tech Stack

- **Core Programming**: Python 3.11+
- **Data Manipulation & Workflows**: Pandas, NumPy
- **Data Warehouse & Database**: PostgreSQL 16, SQL (Analytical & Dimensional Modeling), SQLAlchemy, Alembic
- **Analytics & Visualization**: Power BI (Import & DirectQuery, DAX Modeling, Star Schema)
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
│   - Power BI Dashboards (Import / DirectQuery, DAX KPI calculations)                     │
│   - FastAPI REST Endpoints for real-time pipeline monitoring & orchestration             │
└──────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 Repository Structure

```
.
├── .github/workflows/      # Automated CI/CD workflows
├── dags/                   # Apache Airflow DAGs for pipeline orchestration
├── data/                   # Data directories (raw, processed, quarantine)
├── docs/                   # System documentation & Power BI integration guides
│   └── powerbi_integration_guide.md
├── src/                    # Primary application source code
│   ├── api/                # FastAPI application, routers & security
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

3. **Configure Environment Variables**
   ```bash
   cp .env.example .env
   # Edit .env with your PostgreSQL credentials and database configurations
   ```

4. **Launch Infrastructure via Docker Compose**
   ```bash
   docker-compose up -d --build
   ```

5. **Run FastAPI Server Locally**
   ```bash
   uvicorn src.api.main:app --reload --port 8000
   ```
   Access API documentation at `http://localhost:8000/docs`.

---

## 🧪 Testing & Quality Assurance

Run the comprehensive unit and integration test suite using `pytest`:

```bash
pytest -v --tb=short
```

---

## 📊 Power BI Analytics & Dashboards

For detailed guidance on connecting **Power BI Desktop & Power BI Service** to the PostgreSQL Data Warehouse, adding DAX KPI measures, and building executive dashboards, see the [Power BI Integration Guide](docs/powerbi_integration_guide.md).

---

## 📄 License

This project is released under the MIT License.
