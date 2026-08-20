import time
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import duckdb
import polars as pl
from src.config.settings import settings
from src.utils.logger import export_logger as logger
from src.transformation.schemas import MedallionLayer, TransformationSummary


class MedallionTransformer:
    """
    In-Process Medallion Pipeline Transformer powered by DuckDB & Polars.
    Executes Bronze -> Silver -> Gold data modeling directly against Parquet files.
    """

    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or settings.STORAGE_PROCESSED_PATH
        self.bronze_dir = self.base_dir / "bronze"
        self.silver_dir = self.base_dir / "silver"
        self.gold_dir = self.base_dir / "gold"

        for d in [self.bronze_dir, self.silver_dir, self.gold_dir]:
            d.mkdir(parents=True, exist_ok=True)

        self.con = duckdb.connect(database=":memory:")

    def process_bronze(self, dataset_name: str, raw_parquet_path: Path) -> TransformationSummary:
        """
        BRONZE LAYER: Raw Staging append-only layer with lineage tracking metadata.
        """
        start_time = time.time()
        output_path = self.bronze_dir / f"{dataset_name}_bronze.parquet"

        # DuckDB Query adding lineage metadata
        query = f"""
            SELECT 
                *, 
                '{raw_parquet_path.name}' AS _raw_source_file,
                CURRENT_TIMESTAMP AS _ingested_at
            FROM read_parquet('{raw_parquet_path}')
        """
        df_bronze = self.con.execute(query).pl()
        df_bronze.write_parquet(output_path)

        exec_time = time.time() - start_time
        logger.info(f"[BRONZE] Created {dataset_name} ({len(df_bronze)} records) -> {output_path}")

        return TransformationSummary(
            dataset_name=dataset_name,
            layer=MedallionLayer.BRONZE,
            input_records=len(df_bronze),
            output_records=len(df_bronze),
            output_file_path=str(output_path.absolute()),
            execution_time_seconds=round(exec_time, 3)
        )

    def process_silver(
        self,
        dataset_name: str,
        bronze_parquet_path: Path,
        primary_keys: Optional[list[str]] = None
    ) -> TransformationSummary:
        """
        SILVER LAYER: Standardized, deduplicated, and cleansed dataset.
        Normalizes column names to lowercase snake_case, removes exact duplicates, and trims strings.
        """
        start_time = time.time()
        output_path = self.silver_dir / f"{dataset_name}_silver.parquet"

        # Read bronze dataset
        df = pl.read_parquet(bronze_parquet_path)
        input_count = len(df)

        # Step 1: Standardize column names (snake_case)
        rename_map = {col: col.strip().lower().replace(" ", "_") for col in df.columns}
        df = df.rename(rename_map)

        # Step 2: Trim string columns
        string_cols = [col for col, dtype in df.schema.items() if dtype == pl.String]
        if string_cols:
            df = df.with_columns([pl.col(c).str.strip_chars() for c in string_cols])

        # Step 3: Deduplication
        if primary_keys:
            pk_normalized = [k.strip().lower().replace(" ", "_") for k in primary_keys]
            dedup_df = df.unique(subset=pk_normalized, keep="last")
        else:
            dedup_df = df.unique()

        dropped_dups = input_count - len(dedup_df)

        # Write to Silver storage
        dedup_df.write_parquet(output_path)
        exec_time = time.time() - start_time

        logger.info(
            f"[SILVER] Cleansed {dataset_name} ({len(dedup_df)} records, {dropped_dups} dups removed) -> {output_path}"
        )

        return TransformationSummary(
            dataset_name=dataset_name,
            layer=MedallionLayer.SILVER,
            input_records=input_count,
            output_records=len(dedup_df),
            dropped_duplicates=dropped_dups,
            output_file_path=str(output_path.absolute()),
            execution_time_seconds=round(exec_time, 3)
        )

    def process_gold(self, dataset_name: str, silver_parquet_path: Path) -> TransformationSummary:
        """
        GOLD LAYER: Aggregated Star-Schema Analytical Dataset.
        Computes business KPIs, metrics summary, and aggregations.
        """
        start_time = time.time()
        output_path = self.gold_dir / f"{dataset_name}_gold_summary.parquet"

        # DuckDB execution for dynamic aggregation
        # If columns contain 'status' and 'amount', group by status
        df_silver = pl.read_parquet(silver_parquet_path)
        cols = [c.lower() for c in df_silver.columns]

        if "status" in cols and "amount" in cols:
            query = f"""
                SELECT 
                    status,
                    COUNT(*) AS total_orders,
                    SUM(amount) AS total_revenue,
                    AVG(amount) AS avg_order_value,
                    MIN(amount) AS min_order_value,
                    MAX(amount) AS max_order_value,
                    CURRENT_TIMESTAMP AS _aggregated_at
                FROM read_parquet('{silver_parquet_path}')
                GROUP BY status
                ORDER BY total_revenue DESC
            """
        else:
            query = f"""
                SELECT 
                    *,
                    CURRENT_TIMESTAMP AS _aggregated_at
                FROM read_parquet('{silver_parquet_path}')
            """

        df_gold = self.con.execute(query).pl()
        df_gold.write_parquet(output_path)

        exec_time = time.time() - start_time
        logger.info(f"[GOLD] Created aggregated Gold dataset {dataset_name} ({len(df_gold)} rows) -> {output_path}")

        return TransformationSummary(
            dataset_name=dataset_name,
            layer=MedallionLayer.GOLD,
            input_records=len(df_silver),
            output_records=len(df_gold),
            output_file_path=str(output_path.absolute()),
            execution_time_seconds=round(exec_time, 3)
        )
