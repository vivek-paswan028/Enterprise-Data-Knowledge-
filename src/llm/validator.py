import re
import sqlparse
from sqlparse.tokens import Keyword, DDL, DML
from src.llm.schemas import SQLValidationReport
from src.utils.logger import export_logger as logger


class SQLSecurityValidator:
    """
    Abstract Syntax Tree (AST) & Lexical Security Validator for LLM Generated SQL.
    Enforces strict read-only execution guardrails to prevent SQL Injection
    and destructive database commands (DROP, DELETE, UPDATE, TRUNCATE, ALTER).
    """

    DISALLOWED_KEYWORDS = {
        "DROP", "DELETE", "UPDATE", "INSERT", "TRUNCATE", "ALTER",
        "GRANT", "REVOKE", "EXEC", "EXECUTE", "CREATE", "REPLACE",
        "VACUUM", "COPY", "MERGE"
    }

    @classmethod
    def validate_sql(cls, sql_query: str) -> SQLValidationReport:
        clean_sql = sql_query.strip().rstrip(";")
        violations = []

        if not clean_sql:
            return SQLValidationReport(is_safe=False, statement_type="EMPTY", violations=["Query is empty."])

        # Check 1: Multi-statement attack check (semicolons separating multiple commands)
        statements = sqlparse.split(sql_query)
        if len(statements) > 1:
            violations.append("Multiple SQL statements detected in a single query payload.")

        parsed = sqlparse.parse(clean_sql)
        if not parsed:
            return SQLValidationReport(is_safe=False, statement_type="INVALID", violations=["Failed to parse SQL AST."])

        stmt = parsed[0]
        stmt_type = stmt.get_type()

        # Check 2: Must be SELECT statement
        if stmt_type != "SELECT":
            violations.append(f"Disallowed SQL statement type '{stmt_type}'. Only 'SELECT' is permitted.")

        # Check 3: AST Token Walk for prohibited DDL/DML keywords
        for token in stmt.flatten():
            token_val = token.value.upper()
            if token_val in cls.DISALLOWED_KEYWORDS:
                violations.append(f"Forbidden keyword '{token_val}' detected in query.")

        # Check 4: Check for comment injection attempts
        if re.search(r"(--|/\*|\*/)", sql_query):
            violations.append("SQL comment characters ('--', '/*') are prohibited.")

        is_safe = len(violations) == 0
        if not is_safe:
            logger.warning(f"SQL Security Violation: {violations} | Query: '{sql_query}'")

        return SQLValidationReport(
            is_safe=is_safe,
            statement_type=stmt_type,
            violations=violations
        )
