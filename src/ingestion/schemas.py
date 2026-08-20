from enum import Enum
from typing import Dict, List, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class SupportedFormat(str, Enum):
    CSV = "csv"
    EXCEL = "excel"
    JSON = "json"
    SQL_DUMP = "sql_dump"


class DriftType(str, Enum):
    NO_DRIFT = "no_drift"
    NEW_COLUMNS = "new_columns"
    MISSING_COLUMNS = "missing_columns"
    TYPE_MISMATCH = "type_mismatch"
    BREAKING_DRIFT = "breaking_drift"


class ColumnSchema(BaseModel):
    name: str
    data_type: str
    is_nullable: bool = True


class SchemaFingerprint(BaseModel):
    dataset_name: str
    signature_hash: str
    column_count: int
    columns: Dict[str, str]  # {column_name: data_type}
    created_at: datetime = Field(default_factory=datetime.utcnow)


class DriftReport(BaseModel):
    dataset_name: str
    drift_type: DriftType
    is_breaking: bool
    added_columns: List[str] = Field(default_factory=list)
    removed_columns: List[str] = Field(default_factory=list)
    type_changes: Dict[str, Dict[str, str]] = Field(default_factory=dict)  # col: {old: x, new: y}
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class IngestionPayload(BaseModel):
    file_name: str
    file_format: SupportedFormat
    raw_file_path: str
    record_count: int
    schema_fingerprint: SchemaFingerprint
    drift_report: Optional[DriftReport] = None
    staged_parquet_path: Optional[str] = None
    ingested_at: datetime = Field(default_factory=datetime.utcnow)
