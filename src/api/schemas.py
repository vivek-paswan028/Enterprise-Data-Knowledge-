from typing import Dict, List, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int


class UploadResponse(BaseModel):
    dataset_name: str
    file_name: str
    file_format: str
    record_count: int
    drift_type: str
    is_breaking_drift: bool
    quality_score: float
    is_valid: bool
    staged_parquet_path: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)


class PipelineRunResponse(BaseModel):
    status: str
    message: str
    execution_time_seconds: float
    layers_processed: List[str]


class KPISummaryResponse(BaseModel):
    total_records: int
    total_revenue: float
    avg_order_value: float
    metrics_by_status: List[Dict[str, Any]]
