from typing import Dict, List, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    natural_language_query: str = Field(
        ...,
        json_schema_extra={"example": "What is the total revenue generated from completed orders by city?"}
    )


class SQLValidationReport(BaseModel):
    is_safe: bool
    statement_type: str
    violations: List[str] = Field(default_factory=list)


class QueryResponse(BaseModel):
    question: str
    generated_sql: str
    is_safe: bool
    validation_message: str
    columns: List[str] = Field(default_factory=list)
    rows: List[Dict[str, Any]] = Field(default_factory=list)
    row_count: int = 0
    executed_at: datetime = Field(default_factory=datetime.utcnow)
