import re
import io
from pathlib import Path
from typing import Dict, Any, List, Union
import polars as pl
import pandas as pd
from src.utils.logger import export_logger as logger
from src.ingestion.schemas import SupportedFormat


class MultiFormatParser:
    """
    High-Performance Unified Data Parser.
    Leverages Polars vectorized engine for CSV/JSON payloads, and Pandas/openpyxl for multi-tab Excel/SQL dumps.
    Converts all raw formats into standardized Polars DataFrames for memory optimization downstream.
    """

    @staticmethod
    def parse_file(file_path: Union[str, Path], file_format: SupportedFormat) -> Dict[str, pl.DataFrame]:
        """
        Parses raw payload into a dictionary of sheet_name/table_name -> Polars DataFrame.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Source data file does not exist: {path.absolute()}")

        logger.info(f"Parsing raw file: {path.name} (Format: {file_format.value})")

        try:
            if file_format == SupportedFormat.CSV:
                return {"default": MultiFormatParser._parse_csv(path)}
            elif file_format == SupportedFormat.EXCEL:
                return MultiFormatParser._parse_excel(path)
            elif file_format == SupportedFormat.JSON:
                return {"default": MultiFormatParser._parse_json(path)}
            elif file_format == SupportedFormat.SQL_DUMP:
                return {"default": MultiFormatParser._parse_sql_dump(path)}
            else:
                raise ValueError(f"Unsupported file format provided: {file_format}")
        except Exception as e:
            logger.error(f"Failed to parse file {path.name}: {str(e)}")
            raise e

    @staticmethod
    def _parse_csv(path: Path) -> pl.DataFrame:
        """Vectorized Polars CSV reader with infer_schema_length."""
        return pl.read_csv(
            path,
            infer_schema_length=10000,
            ignore_errors=False,
            truncate_ragged_lines=True
        )

    @staticmethod
    def _parse_excel(path: Path) -> Dict[str, pl.DataFrame]:
        """Multi-sheet Excel parser using Pandas openpyxl backend, converted to Polars."""
        excel_file = pd.ExcelFile(path, engine="openpyxl")
        sheets_dict = {}
        for sheet in excel_file.sheet_names:
            df_pandas = pd.read_excel(excel_file, sheet_name=sheet)
            # Standardize column names to string type
            df_pandas.columns = [str(col).strip() for col in df_pandas.columns]
            sheets_dict[sheet] = pl.from_pandas(df_pandas)
        return sheets_dict

    @staticmethod
    def _parse_json(path: Path) -> pl.DataFrame:
        """Parses JSON line-delimited or structured JSON arrays into Polars DataFrame."""
        try:
            # Try parsing as JSON array / object first
            return pl.read_json(path)
        except Exception:
            # Fallback to NDJSON (Newline Delimited JSON)
            return pl.read_ndjson(path)

    @staticmethod
    def _parse_sql_dump(path: Path) -> pl.DataFrame:
        """
        Parses SQL Dumps containing standard INSERT INTO statements.
        Extracts column names and values using Regex parsing.
        """
        content = path.read_text(encoding="utf-8", errors="ignore")

        # Find INSERT INTO statements
        insert_pattern = re.compile(
            r"INSERT\s+INTO\s+[`\"']?(\w+)[`\"']?\s*\(([^)]+)\)\s*VALUES\s*(.+?);",
            re.IGNORECASE | re.DOTALL
        )
        matches = insert_pattern.findall(content)

        if not matches:
            raise ValueError(f"No valid INSERT INTO statements found in SQL dump: {path.name}")

        columns = []
        all_rows = []

        for match in matches:
            table_name, cols_str, values_str = match
            if not columns:
                columns = [c.strip(" `\"'") for c in cols_str.split(",")]

            # Extract individual row value tuples: (val1, val2, ...)
            row_pattern = re.compile(r"\((.*?)\)(?:,\s*|\s*$)", re.DOTALL)
            rows = row_pattern.findall(values_str)

            for r in rows:
                parsed_row = [val.strip().strip("'\"") for val in r.split(",")]
                if len(parsed_row) == len(columns):
                    all_rows.append(parsed_row)

        if not all_rows:
            raise ValueError(f"Failed to extract structured row data from SQL dump: {path.name}")

        # Construct Pandas DataFrame and convert to Polars
        df_pd = pd.DataFrame(all_rows, columns=columns)
        return pl.from_pandas(df_pd)
