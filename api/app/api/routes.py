from fastapi import APIRouter, HTTPException
from services.langchain_service import LangChainService
from services.langchain_service_warehouse import LangChainServiceWarehouse
# from services.database_service import DatabaseService

router = APIRouter()
langchain_service = LangChainService()
langchain_service_warehouse = LangChainServiceWarehouse()
# database_service = DatabaseService()

@router.post("/query")
async def query(text: str):
    try:
        sql_query = langchain_service.text_to_sql(text)
        # result = database_service.execute_sql(sql_query)
        return sql_query
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.post("/query_warehouse")
async def query_warehouse(text: str):
    try:
        sql_query = langchain_service_warehouse.text_to_sql(text)
        # result = database_service.execute_sql(sql_query)
        return sql_query
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))