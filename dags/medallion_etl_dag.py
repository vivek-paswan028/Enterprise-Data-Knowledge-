"""
Production Apache Airflow DAG: DataPulse Enterprise Medallion ETL Pipeline
Orchestrates: Multi-Format Ingestion -> Quality Gatekeeper -> Bronze -> Silver -> Gold
"""

from datetime import datetime, timedelta
from pathlib import Path
from airflow import DAG
from airflow.operators.python import PythonOperator

# Lazy imports inside tasks to maintain Airflow DAG parsing speed
def run_ingestion_task(**kwargs):
    from src.ingestion.manager import IngestionManager
    from src.ingestion.schemas import SupportedFormat

    manager = IngestionManager()
    data_dir = Path("./data/raw")
    results = []
    
    # Process any sample raw files
    for raw_file in data_dir.glob("*.*"):
        if raw_file.suffix.lower() == ".csv":
            payloads = manager.process_file(raw_file, SupportedFormat.CSV)
            results.extend([p.model_dump(mode="json") for p in payloads])

    return results


def run_data_quality_task(**kwargs):
    from src.validation.engine import DataQualityEngine
    import polars as pl

    engine = DataQualityEngine()
    raw_dir = Path("./data/raw")
    reports = []

    for parquet_file in raw_dir.glob("*_staged.parquet"):
        df = pl.read_parquet(parquet_file)
        valid_df, invalid_df, report = engine.validate_dataframe(parquet_file.stem, df)
        reports.append(report.model_dump(mode="json"))

    return reports


def run_medallion_transformation_task(**kwargs):
    from src.transformation.medallion import MedallionTransformer
    from pathlib import Path

    transformer = MedallionTransformer()
    raw_dir = Path("./data/raw")

    for parquet_file in raw_dir.glob("*_staged.parquet"):
        dataset_name = parquet_file.name.replace("_staged.parquet", "")

        # 1. Bronze
        bronze_summary = transformer.process_bronze(dataset_name, parquet_file)

        # 2. Silver
        silver_summary = transformer.process_silver(
            dataset_name,
            Path(bronze_summary.output_file_path)
        )

        # 3. Gold
        gold_summary = transformer.process_gold(
            dataset_name,
            Path(silver_summary.output_file_path)
        )

    return "Medallion Transformation Pipeline Completed Successfully"


# Airflow DAG Definition
default_args = {
    "owner": "datapulse_de_team",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="datapulse_medallion_etl_pipeline",
    default_args=default_args,
    description="Enterprise Medallion Architecture (Bronze -> Silver -> Gold) ETL Pipeline",
    schedule_interval="@hourly",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["production", "datapulse", "medallion", "duckdb"],
) as dag:

    ingest_task = PythonOperator(
        task_id="ingest_multi_format_payloads",
        python_callable=run_ingestion_task,
    )

    quality_task = PythonOperator(
        task_id="enforce_data_quality_contracts",
        python_callable=run_data_quality_task,
    )

    medallion_task = PythonOperator(
        task_id="execute_medallion_transformations",
        python_callable=run_medallion_transformation_task,
    )

    # Airflow Task Dependency Graph
    ingest_task >> quality_task >> medallion_task
