from fastapi import APIRouter, HTTPException
from services.langchain_service import LangChainService
from services.langchain_service_warehouse import LangChainServiceWarehouse
# from services.database_service import DatabaseService

human_input = False

def on_human_input() -> str:
    global human_input
    human_input = True

    

router = APIRouter()
langchain_service = LangChainService(on_human_input=on_human_input)
langchain_service_warehouse = LangChainServiceWarehouse(on_human_input=on_human_input)
# database_service = DatabaseService()



@router.post("/query")
async def query(sentence: str):
    print("sentence: ", sentence)
    try:
        # global human_input
        # if human_input: # if human input is not empty, it means our query is a follow-up query to the human input request
        #     human_input = False
        #     return langchain_service.text_to_sql(human_input) 

        sql_query = langchain_service.text_to_sql(sentence)
        
        # result = database_service.execute_sql(sql_query)
        
        if human_input:
            return human_input
        else:
            return sql_query
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.get("/poke")
async def poke_llm(type: str):
    try:
        if type == "warehouse":
            sql_query = langchain_service_warehouse.initial_poke()

        sql_query = langchain_service.initial_poke()

        return sql_query

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 

@router.post("/query_warehouse")
async def query_warehouse(sentence: str):
    try:
        # global human_input
        # if human_input != "": # if human input is not empty, it means our query is a follow-up query to the human input request
        #     temp_input = human_input
        #     human_input = ""
        #     return langchain_service_warehouse.text_to_sql(temp_input)
        
        sql_query = langchain_service_warehouse.text_to_sql(sentence)
        # result = database_service.execute_sql(sql_query)
        
        if  human_input:
            return human_input
        else:
            return  sql_query
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))