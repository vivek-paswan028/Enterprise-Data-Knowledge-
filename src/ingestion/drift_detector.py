import json
import hashlib
from pathlib import Path
from typing import Dict, Optional, Tuple, Any
import polars as pl
from src.utils.logger import export_logger as logger
from src.ingestion.schemas import (
    SchemaFingerprint,
    DriftReport,
    DriftType,
)


class SchemaFingerprinter:
    """
    Computes deterministic SHA-256 cryptographic fingerprints of DataFrame schemas.
    The fingerprint signature incorporates column order, column names, and Polars data types.
    """

    @staticmethod
    def compute_fingerprint(dataset_name: str, df: pl.DataFrame) -> SchemaFingerprint:
        # Extract column schema: {column_name: str_data_type}
        schema_dict = {col: str(dtype) for col, dtype in df.schema.items()}

        # Sort columns to create canonical representation for hashing
        canonical_representation = json.dumps(sorted(schema_dict.items()), sort_keys=True)
        signature_hash = hashlib.sha256(canonical_representation.encode("utf-8")).hexdigest()

        return SchemaFingerprint(
            dataset_name=dataset_name,
            signature_hash=signature_hash,
            column_count=len(df.columns),
            columns=schema_dict,
        )


class MetadataRegistry:
    """
    Persists and retrieves registered dataset schema fingerprints.
    Uses file-based JSON storage (can easily swap to PostgreSQL metadata table downstream).
    """

    def __init__(self, registry_path: Path = Path("./data/metadata_registry.json")):
        self.registry_path = registry_path
        self._ensure_registry_exists()

    def _ensure_registry_exists(self) -> None:
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.registry_path.exists():
            with open(self.registry_path, "w", encoding="utf-8") as f:
                json.dump({}, f)

    def get_registered_schema(self, dataset_name: str) -> Optional[SchemaFingerprint]:
        with open(self.registry_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if dataset_name in data:
            return SchemaFingerprint(**data[dataset_name])
        return None

    def register_schema(self, fingerprint: SchemaFingerprint) -> None:
        with open(self.registry_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        data[fingerprint.dataset_name] = fingerprint.model_dump(mode="json")

        with open(self.registry_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Registered schema fingerprint for dataset: '{fingerprint.dataset_name}' [Hash: {fingerprint.signature_hash[:8]}]")


class SchemaDriftDetector:
    """
    Detects non-breaking and breaking schema drift between incoming payload and registered metadata.
    """

    @staticmethod
    def evaluate_drift(
        incoming_fingerprint: SchemaFingerprint,
        baseline_fingerprint: Optional[SchemaFingerprint]
    ) -> DriftReport:
        # Scenario 1: First time ingesting this dataset -> No Baseline -> Initial Schema
        if not baseline_fingerprint:
            logger.info(f"First ingestion for dataset '{incoming_fingerprint.dataset_name}'. Setting baseline schema.")
            return DriftReport(
                dataset_name=incoming_fingerprint.dataset_name,
                drift_type=DriftType.NO_DRIFT,
                is_breaking=False,
                message="Initial schema registration. Baseline created."
            )

        # Scenario 2: Identical Fingerprint -> Zero Drift
        if incoming_fingerprint.signature_hash == baseline_fingerprint.signature_hash:
            return DriftReport(
                dataset_name=incoming_fingerprint.dataset_name,
                drift_type=DriftType.NO_DRIFT,
                is_breaking=False,
                message="Incoming schema matches baseline exactly."
            )

        # Scenario 3: Schema Difference Analysis
        incoming_cols = set(incoming_fingerprint.columns.keys())
        baseline_cols = set(baseline_fingerprint.columns.keys())

        added_columns = list(incoming_cols - baseline_cols)
        removed_columns = list(baseline_cols - incoming_cols)

        type_changes = {}
        common_cols = incoming_cols.intersection(baseline_cols)
        for col in common_cols:
            incoming_type = incoming_fingerprint.columns[col]
            baseline_type = baseline_fingerprint.columns[col]
            if incoming_type != baseline_type:
                type_changes[col] = {"baseline": baseline_type, "incoming": incoming_type}

        # Classify severity:
        # Breaking Drift = Removed Columns OR Incompatible Data Type Changes
        is_breaking = len(removed_columns) > 0 or len(type_changes) > 0

        if is_breaking:
            drift_type = DriftType.BREAKING_DRIFT
            msg = f"BREAKING DRIFT DETECTED: {len(removed_columns)} column(s) missing, {len(type_changes)} type mismatch(es)."
            logger.warning(f"[{incoming_fingerprint.dataset_name}] {msg}")
        elif len(added_columns) > 0:
            drift_type = DriftType.NEW_COLUMNS
            msg = f"NON-BREAKING DRIFT: {len(added_columns)} new column(s) appended."
            logger.info(f"[{incoming_fingerprint.dataset_name}] {msg}")
        else:
            drift_type = DriftType.NO_DRIFT
            msg = "Schema modified (reordered columns or formatting change)."

        return DriftReport(
            dataset_name=incoming_fingerprint.dataset_name,
            drift_type=drift_type,
            is_breaking=is_breaking,
            added_columns=added_columns,
            removed_columns=removed_columns,
            type_changes=type_changes,
            message=msg
        )
