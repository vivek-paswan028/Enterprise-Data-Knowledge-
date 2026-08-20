from enum import Enum
from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class MedallionLayer(str, Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"


class TransformationSummary(BaseModel):
    dataset_name: str
    layer: MedallionLayer
    input_records: int
    output_records: int
    dropped_duplicates: int = 0
    nulls_imputed: int = 0
    output_file_path: str
    execution_time_seconds: float
    processed_at: datetime = Field(default_factory=datetime.utcnow)
