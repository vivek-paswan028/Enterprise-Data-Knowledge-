from typing import Dict, List, Tuple, Optional, Any
import polars as pl
from src.utils.logger import export_logger as logger
from src.validation.schemas import (
    ExpectationRule,
    ExpectationSuiteConfig,
    ValidationCheckResult,
    DataQualityReport,
    ValidationSeverity
)
from src.validation.quarantine import QuarantineHandler


class DataQualityEngine:
    """
    Enterprise Data Quality Validation Engine.
    Executes declarative quality expectations on incoming DataFrames, builds audit reports,
    and quarantines invalid rows before Medallion pipeline loading.
    """

    def __init__(self, quarantine_handler: Optional[QuarantineHandler] = None):
        self.quarantine_handler = quarantine_handler or QuarantineHandler()

    @staticmethod
    def generate_default_suite(dataset_name: str, df: pl.DataFrame) -> ExpectationSuiteConfig:
        """
        Auto-generates a default Great Expectations suite based on DataFrame schema profiling.
        """
        rules = []

        for col, dtype in df.schema.items():
            # Rule 1: Non-null checks for primary keys / ID fields
            if col.endswith("_id") or col == "id":
                rules.append(ExpectationRule(
                    rule_name=f"non_null_{col}",
                    column=col,
                    expectation_type="expect_column_values_to_not_be_null",
                    severity=ValidationSeverity.CRITICAL
                ))
                rules.append(ExpectationRule(
                    rule_name=f"unique_{col}",
                    column=col,
                    expectation_type="expect_column_values_to_be_unique",
                    severity=ValidationSeverity.WARNING
                ))
            # Rule 2: Non-negative numerical check for amounts/prices
            elif any(k in col.lower() for k in ["amount", "price", "cost", "salary", "revenue"]):
                rules.append(ExpectationRule(
                    rule_name=f"non_negative_{col}",
                    column=col,
                    expectation_type="expect_column_values_to_be_between",
                    kwargs={"min_value": 0},
                    severity=ValidationSeverity.CRITICAL
                ))

        return ExpectationSuiteConfig(dataset_name=dataset_name, rules=rules)

    def validate_dataframe(
        self,
        dataset_name: str,
        df: pl.DataFrame,
        suite_config: Optional[ExpectationSuiteConfig] = None
    ) -> Tuple[pl.DataFrame, pl.DataFrame, DataQualityReport]:

        if suite_config is None:
            suite_config = self.generate_default_suite(dataset_name, df)

        total_records = len(df)
        check_results: List[ValidationCheckResult] = []
        invalid_mask = pl.lit(False)

        logger.info(f"Executing Data Quality suite with {len(suite_config.rules)} rule(s) for dataset '{dataset_name}'")

        for rule in suite_config.rules:
            if rule.column not in df.columns:
                check_results.append(ValidationCheckResult(
                    rule_name=rule.rule_name,
                    column=rule.column,
                    expectation_type=rule.expectation_type,
                    success=False,
                    severity=rule.severity,
                    details=f"Column '{rule.column}' is missing from payload"
                ))
                continue

            rule_invalid_mask = pl.lit(False)

            if rule.expectation_type == "expect_column_values_to_not_be_null":
                rule_invalid_mask = df[rule.column].is_null()

            elif rule.expectation_type == "expect_column_values_to_be_between":
                min_val = rule.kwargs.get("min_value")
                max_val = rule.kwargs.get("max_value")

                col_expr = df[rule.column]
                if min_val is not None and max_val is not None:
                    rule_invalid_mask = (col_expr < min_val) | (col_expr > max_val)
                elif min_val is not None:
                    rule_invalid_mask = (col_expr < min_val)
                elif max_val is not None:
                    rule_invalid_mask = (col_expr > max_val)

            elif rule.expectation_type == "expect_column_values_to_be_unique":
                # Mark duplicated values as invalid
                rule_invalid_mask = df[rule.column].is_duplicated()

            # Filter non-null entries from invalid condition where appropriate
            rule_invalid_mask = rule_invalid_mask.fill_null(False)

            unexpected_df = df.filter(rule_invalid_mask)
            unexpected_count = len(unexpected_df)
            unexpected_percent = (unexpected_count / total_records * 100) if total_records > 0 else 0.0
            unexpected_samples = unexpected_df[rule.column].head(5).to_list() if unexpected_count > 0 else []

            success = unexpected_count == 0

            check_results.append(ValidationCheckResult(
                rule_name=rule.rule_name,
                column=rule.column,
                expectation_type=rule.expectation_type,
                success=success,
                unexpected_count=unexpected_count,
                unexpected_percent=round(unexpected_percent, 2),
                unexpected_values=unexpected_samples,
                severity=rule.severity
            ))

            if rule.severity == ValidationSeverity.CRITICAL:
                invalid_mask = invalid_mask | rule_invalid_mask

        # Separate clean records from quarantined invalid records
        valid_df = df.filter(~invalid_mask)
        invalid_df = df.filter(invalid_mask)

        failed_records = len(invalid_df)
        passed_records = len(valid_df)
        is_valid = failed_records == 0
        overall_score = round((passed_records / total_records * 100), 2) if total_records > 0 else 100.0

        quarantine_path_str = None
        report = DataQualityReport(
            dataset_name=dataset_name,
            total_records=total_records,
            passed_records=passed_records,
            failed_records=failed_records,
            is_valid=is_valid,
            overall_score=overall_score,
            results=check_results
        )

        if failed_records > 0:
            quarantine_path = self.quarantine_handler.quarantine_records(dataset_name, invalid_df, report)
            report.quarantine_path = str(quarantine_path.absolute())

        logger.info(
            f"Quality Check Completed for '{dataset_name}': {passed_records}/{total_records} passed ({overall_score}%)"
        )
        return valid_df, invalid_df, report
