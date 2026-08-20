from enum import Enum
from typing import Dict, List, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class ValidationSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class ExpectationRule(BaseModel):
    rule_name: str
    column: str
    expectation_type: str  # e.g., "expect_column_values_to_not_be_null", "expect_column_values_to_be_between"
    kwargs: Dict[str, Any] = Field(default_factory=dict)
    severity: ValidationSeverity = ValidationSeverity.CRITICAL


class ExpectationSuiteConfig(BaseModel):
    dataset_name: str
    rules: List[ExpectationRule]


class ValidationCheckResult(BaseModel):
    rule_name: str
    column: str
    expectation_type: str
    success: bool
    unexpected_count: int = 0
    unexpected_percent: float = 0.0
    unexpected_values: List[Any] = Field(default_factory=list)
    severity: ValidationSeverity
    details: Optional[str] = None


class DataQualityReport(BaseModel):
    dataset_name: str
    total_records: int
    passed_records: int
    failed_records: int
    is_valid: bool
    overall_score: float  # Percentage of passing records/rules
    results: List[ValidationCheckResult]
    quarantine_path: Optional[str] = None
    validated_at: datetime = Field(default_factory=datetime.utcnow)
