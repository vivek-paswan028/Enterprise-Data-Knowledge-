from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status
import polars as pl
from src.config.settings import settings
from src.api.schemas import UploadResponse
from src.api.security import get_current_user, TokenData
from src.ingestion.schemas import SupportedFormat
from src.ingestion.manager import IngestionManager
from src.validation.engine import DataQualityEngine

router = APIRouter(prefix="/api/v1/data", tags=["Data Ingestion & Quality"])


@router.post("/upload", response_model=List[UploadResponse])
async def upload_raw_data_file(
    file: UploadFile = File(...),
    dataset_name: Optional[str] = Form(None),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Multi-Format Data Ingestion Endpoint.
    Parses CSV, Excel, JSON, or SQL Dumps, performs schema drift detection,
    executes Data Quality validation suites, and stages data as Parquet.
    """
    file_ext = Path(file.filename).suffix.lower()
    format_map = {
        ".csv": SupportedFormat.CSV,
        ".xlsx": SupportedFormat.EXCEL,
        ".xls": SupportedFormat.EXCEL,
        ".json": SupportedFormat.JSON,
        ".sql": SupportedFormat.SQL_DUMP
    }

    if file_ext not in format_map:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file extension '{file_ext}'. Supported: .csv, .xlsx, .json, .sql"
        )

    file_format = format_map[file_ext]
    temp_save_path = settings.STORAGE_RAW_PATH / file.filename

    # Save uploaded file bytes
    content = await file.read()
    with open(temp_save_path, "wb") as f:
        f.write(content)

    # 1. Run Ingestion Manager
    ingestion_manager = IngestionManager()
    payloads = ingestion_manager.process_file(temp_save_path, file_format, dataset_name=dataset_name)

    # 2. Run Data Quality Engine
    quality_engine = DataQualityEngine()
    responses = []

    for payload in payloads:
        staged_df = pl.read_parquet(payload.staged_parquet_path)
        valid_df, invalid_df, quality_report = quality_engine.validate_dataframe(
            payload.schema_fingerprint.dataset_name,
            staged_df
        )

        responses.append(UploadResponse(
            dataset_name=payload.schema_fingerprint.dataset_name,
            file_name=file.filename,
            file_format=file_format.value,
            record_count=payload.record_count,
            drift_type=payload.drift_report.drift_type if payload.drift_report else "no_drift",
            is_breaking_drift=payload.drift_report.is_breaking if payload.drift_report else False,
            quality_score=quality_report.overall_score,
            is_valid=quality_report.is_valid,
            staged_parquet_path=payload.staged_parquet_path
        ))

    return responses
