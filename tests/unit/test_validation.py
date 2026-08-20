import pytest
from pathlib import Path
import polars as pl
from src.validation.schemas import (
    ExpectationRule,
    ExpectationSuiteConfig,
    ValidationSeverity
)
from src.validation.quarantine import QuarantineHandler
from src.validation.engine import DataQualityEngine


@pytest.fixture
def sample_orders_df() -> pl.DataFrame:
    return pl.DataFrame({
        "order_id": [101, 102, None, 104, 105],
        "customer_id": ["C1", "C2", "C3", "C4", "C5"],
        "amount": [250.0, -50.0, 100.0, 500.0, 0.0],
        "status": ["COMPLETED", "PENDING", "FAILED", "COMPLETED", "CANCELLED"]
    })


def test_default_suite_generation(sample_orders_df: pl.DataFrame):
    suite = DataQualityEngine.generate_default_suite("orders", sample_orders_df)
    assert suite.dataset_name == "orders"
    rule_names = [r.rule_name for r in suite.rules]
    assert "non_null_order_id" in rule_names
    assert "non_negative_amount" in rule_names


def test_validation_engine_execution(sample_orders_df: pl.DataFrame, tmp_path: Path):
    quarantine_handler = QuarantineHandler(quarantine_dir=tmp_path / "quarantine")
    engine = DataQualityEngine(quarantine_handler=quarantine_handler)

    suite = ExpectationSuiteConfig(
        dataset_name="orders",
        rules=[
            ExpectationRule(
                rule_name="non_null_order_id",
                column="order_id",
                expectation_type="expect_column_values_to_not_be_null",
                severity=ValidationSeverity.CRITICAL
            ),
            ExpectationRule(
                rule_name="non_negative_amount",
                column="amount",
                expectation_type="expect_column_values_to_be_between",
                kwargs={"min_value": 0},
                severity=ValidationSeverity.CRITICAL
            )
        ]
    )

    valid_df, invalid_df, report = engine.validate_dataframe("orders", sample_orders_df, suite)

    assert report.total_records == 5
    # Order ID is null in row 3 (idx 2), amount is negative in row 2 (idx 1) -> 2 invalid rows
    assert len(invalid_df) == 2
    assert len(valid_df) == 3
    assert report.is_valid is False
    assert report.overall_score == 60.0
    assert report.quarantine_path is not None
    assert Path(report.quarantine_path).exists()
