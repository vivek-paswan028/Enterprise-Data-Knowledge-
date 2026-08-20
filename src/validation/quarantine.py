import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
import polars as pl
from src.config.settings import settings
from src.utils.logger import export_logger as logger
from src.validation.schemas import DataQualityReport


class QuarantineHandler:
    """
    Enterprise Data Quarantine Manager.
    Isolates corrupted rows or failing data batches into the quarantine data store data/quarantine/
    with attached error diagnostics for data governance auditing.
    """

    def __init__(self, quarantine_dir: Optional[Path] = None):
        self.quarantine_dir = quarantine_dir or settings.STORAGE_QUARANTINE_PATH
        self.quarantine_dir.mkdir(parents=True, exist_ok=True)

    def quarantine_records(
        self,
        dataset_name: str,
        quarantined_df: pl.DataFrame,
        report: DataQualityReport
    ) -> Path:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        quarantine_filename = f"{dataset_name}_quarantined_{timestamp}.parquet"
        quarantine_path = self.quarantine_dir / quarantine_filename

        # Write corrupted records to Parquet
        quarantined_df.write_parquet(quarantine_path)

        # Write metadata JSON report
        meta_path = self.quarantine_dir / f"{dataset_name}_quarantined_{timestamp}_meta.json"
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(report.model_dump(mode="json"), f, indent=2)

        logger.warning(
            f"Quarantined {len(quarantined_df)} records for dataset '{dataset_name}' to path: {quarantine_path}"
        )
        return quarantine_path
