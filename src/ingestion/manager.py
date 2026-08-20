from pathlib import Path
from typing import Dict, List, Union, Optional
import polars as pl
from src.config.settings import settings
from src.utils.logger import export_logger as logger
from src.ingestion.schemas import (
    SupportedFormat,
    IngestionPayload,
    SchemaFingerprint,
    DriftReport
)
from src.ingestion.parsers import MultiFormatParser
from src.ingestion.drift_detector import (
    SchemaFingerprinter,
    MetadataRegistry,
    SchemaDriftDetector
)


class IngestionManager:
    """
    Orchestrates end-to-end multi-format data ingestion:
    1. Parses CSV, Excel, JSON, or SQL Dumps into Polars DataFrames.
    2. Computes schema cryptographic fingerprint.
    3. Evaluates schema drift against Metadata Registry.
    4. Automatically stages raw data into optimized Parquet format in data/raw/.
    5. Updates metadata registry if drift is non-breaking.
    """

    def __init__(self, registry_path: Optional[Path] = None):
        self.registry = MetadataRegistry(registry_path or (settings.STORAGE_RAW_PATH.parent / "metadata_registry.json"))

    def process_file(
        self,
        file_path: Union[str, Path],
        file_format: SupportedFormat,
        dataset_name: Optional[str] = None
    ) -> List[IngestionPayload]:

        path = Path(file_path)
        ds_name = dataset_name or path.stem.lower()

        # Step 1: Parse multi-format data into dictionary of sheet/table -> Polars DataFrame
        dfs_dict = MultiFormatParser.parse_file(path, file_format)
        results = []

        for sheet_or_table_name, df in dfs_dict.items():
            current_dataset_name = f"{ds_name}_{sheet_or_table_name}" if sheet_or_table_name != "default" else ds_name

            # Step 2: Calculate incoming schema fingerprint
            incoming_fingerprint = SchemaFingerprinter.compute_fingerprint(current_dataset_name, df)

            # Step 3: Fetch baseline schema fingerprint from Registry
            baseline_fingerprint = self.registry.get_registered_schema(current_dataset_name)

            # Step 4: Evaluate schema drift
            drift_report = SchemaDriftDetector.evaluate_drift(incoming_fingerprint, baseline_fingerprint)

            # Step 5: Handle schema persistence decision
            # Stage file to raw parquet storage
            staged_filename = f"{current_dataset_name}_staged.parquet"
            staged_path = settings.STORAGE_RAW_PATH / staged_filename
            df.write_parquet(staged_path)
            logger.info(f"Staged raw dataset '{current_dataset_name}' to Parquet storage: {staged_path}")

            # Register schema if it's the first time OR if non-breaking drift (e.g. columns added)
            if not baseline_fingerprint or not drift_report.is_breaking:
                self.registry.register_schema(incoming_fingerprint)

            payload = IngestionPayload(
                file_name=path.name,
                file_format=file_format,
                raw_file_path=str(path.absolute()),
                record_count=len(df),
                schema_fingerprint=incoming_fingerprint,
                drift_report=drift_report,
                staged_parquet_path=str(staged_path.absolute())
            )
            results.append(payload)

        return results
