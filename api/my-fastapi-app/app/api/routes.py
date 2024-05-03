from fastapi import APIRouter, HTTPException
from ..services.langchain_service import LangChainService
from ..services.database_service import DatabaseService

router = APIRouter()
langchain_service = LangChainService()
database_service = DatabaseService()

@router.post("/query")
async def query(text: str):
    try:
        sql_query = langchain_service.text_to_sql(text)
        result = database_service.execute_sql(sql_query)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))