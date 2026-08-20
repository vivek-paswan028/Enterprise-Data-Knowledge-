from fastapi import APIRouter, Depends, HTTPException, status
from src.api.security import get_current_user, TokenData
from src.llm.schemas import QueryRequest, QueryResponse
from src.llm.engine import TextToSQLEngine

router = APIRouter(prefix="/api/v1/llm", tags=["LLM Natural Language Querying"])


@router.post("/query", response_model=QueryResponse)
async def query_data_warehouse_with_natural_language(
    request: QueryRequest,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Text-to-SQL Natural Language Query Endpoint.
    Translates business questions into AST-validated SELECT queries and returns formatted results.
    """
    if not request.natural_language_query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Natural language query string cannot be empty."
        )

    engine = TextToSQLEngine()
    response = engine.process_query(request.natural_language_query)
    return response
