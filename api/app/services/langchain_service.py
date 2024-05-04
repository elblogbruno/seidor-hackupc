from typing import List, Optional, Union
from langchain.agents import AgentType, initialize_agent, load_tools, create_react_agent, AgentExecutor
import os

from langchain_openai import OpenAI, ChatOpenAI
from langchain_groq import ChatGroq

from langchain_chroma import Chroma
from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,
)
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import PromptTemplate 
from langchain_community.chat_message_histories import SQLChatMessageHistory

from langchain_community.utilities import SQLDatabase
from langchain_core.pydantic_v1 import BaseModel, Field


# from langchain.agents import create_sql_agent 
from langchain.agents.agent_toolkits import SQLDatabaseToolkit 
from langchain.agents.agent_types import AgentType
# from tools.dht11 import get_Dht11
from langchain.tools import BaseTool, StructuredTool, tool

# from langchain.tools.base import StructuredTool

# from langchain_experimental.agents.agent_toolkits import create_csv_agent, create_pandas_dataframe_agent

import pandas as pd

from langchain_core.pydantic_v1 import BaseModel, Field
from fuzzywuzzy import fuzz

from langchain_community.llms import Ollama


class Product(BaseModel):
    id: Optional[Union[str, int]] = Field(description="The product ID")
    name: str = Field(description="The product name")
    ean: Optional[Union[str, int]] = Field(description="The product EAN")
    quantity: Optional[int] = Field(description="The quantity available in the warehouse")


class Order(BaseModel):
    """Extracted data about people."""

    # Creates a model so that we can extract multiple entities.
    people: List[Product]

DBPASS = "test"
DATABASE = "warehouse"

# SQL_PREFIX = """You are an agent designed to interact with a SQL database.
# Given an input question, create a syntactically correct {dialect} query to run, then look at the results of the query and return the answer.
# Always limit your query to at most {top_k} results using the LIMIT clause.
# You can order the results by a relevant column to return the most interesting examples in the database.
# Never query for all the columns from a specific table, only ask for a the few relevant columns given the question.
# If you get a "no such table" error, rewrite your query by using the table in quotes.
# DO NOT use a column name that does not exist in the table.
# You have access to tools for interacting with the database.
# Only use the below tools. Only use the information returned by the below tools to construct your final answer.
# You MUST double check your query before executing it. If you get an error while executing a query, rewrite a different query and try again.
# DO NOT try to execute the query more than three times.
# DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.
# If the question does not seem related to the database, just return "I don't know" as the answer.
# If you cannot find a way to answer the question, just return the best answer you can find after trying at least three times.
# You can also use the internet to find the answer to the question using the "google-search" tool.
# User input will be product names that he wants to order. The agent should return the product ID and the quantity available in the warehouse and add it to {order_list}.
# If the product is not available, the agent should return "Product not available".
# If the product is available, but the quantity is less than the requested quantity, the agent should return "Quantity not available".
# If the product is available and the quantity is equal to or greater than the requested quantity, the agent should return "Product available".
# If the product name is not in the database, the agent should return "Product not found".
# """

SQL_PREFIX = """
You are an agent designed to interact with a .csv file to help an user order products from a warehouse.
{input} will be a product name that he wants to order from the .csv file. 
If product is not found, search the product name that highly matches the user input in the .csv file. If found, add the product to  {order_list}.
The agent should get the product ID, name, ean from .csv and add it to {order_list}.
If quantity is not specified, ask the user for the quantity.
If the product name is not in the database, the agent should return "Product not found".
Only add one product to the order list at a time.
User can also ask to remove a product from the order list or reduce the quantity of a product in the order list.
User can also ask to save the order list to a file.

Always answer returning {order_list} at the end of the answer.

If you are unsure of the next step, show your output and ask user for input.
Do not role play in the conversation. For example, generating AI and Human conversation is not allowed.

"""



SQL_SUFFIX = """Begin!
Question: {input}
Thought: You should always think about what to do
{agent_scratchpad}"""

order_list = []


import json


@tool()
def add_product_to_order_list(name: str, quantity: int = 1) -> str:
    """Add a product to the order list."""
    # Add a product to the order list
    product = search_product(name)

    print(product)


    if product is None:
        return "Product not found"
    
    product["quantity"] = quantity

    order_list.append(product)

    return "Product added to order list"


@tool()
def product_list(query: str = "") -> str:
    """Get the list of products."""
    df = pd.read_csv("/home/brunomoya/development/hackupc/seidor-hackupc/api/app/services/products.csv", delimiter=";")
    product_descriptions = []

    try:
        response = df.to_json(orient="records")
        for item in json.loads(response):
            print(item)
            if 'quantity' not in item:
                item['quantity'] = 0
                
            product_descriptions.append(f"ID: {item['id']}, Name: {item['name']}, EAN: {item['ean']} Quantity: {item['quantity']}")
    except ValueError as e:
        return f"Error parsing JSON: {e}\nResponse text: {response.text}"

    result_string = ', '.join(product_descriptions)

    return result_string

@tool()
def my_list(query: str = "") -> str:
    """Get the current order list."""
    
    # return the current order list as a string
    order_descriptions = []

    try:
        for item in order_list:
            order_descriptions.append(f"ID: {item['id']}, Name: {item['name']}, EAN: {item['ean']} Quantity: {item['quantity']}")
    except ValueError as e:
        return f"Error parsing JSON: {e}"
    
    result_string = ', '.join(order_descriptions)

    return result_string

@tool()
def search_product(product_name: str) -> Product:
    """Search for a product in the product list."""
    df = pd.read_csv("/home/brunomoya/development/hackupc/seidor-hackupc/api/app/services/products.csv", delimiter=";")
    product = df[df["name"].str.contains(product_name, case=False, na=False)].to_dict(orient="records")
    if len(product) > 0:
        return product[0]
    else:
        return None

@tool("similarity", args_schema=Product, return_direct=True)
def similarity(user_input_name: str, product_name: str) -> float:
    """Check the similarity between two strings."""
    # Check the similarity between two strings
    return fuzz.token_sort_ratio(user_input_name, product_name)

@tool()
def remove_product_from_order_list(id: str) -> List[Product]:
    """Remove a product from the order list."""
    # Remove a product from the order list
    order_list_filtered = [item for item in order_list if item["id"] != id]
    return order_list_filtered

@tool()
def save_order_list_tool(query: str = "") -> str:
    """Save the order list to a file."""
    # Save the order list to a file
    with open("order_list.txt", "w") as f:
        for item in order_list:
            f.write("%s\n" % item)

class LangChainService:
    def __init__(self):
        google_api_key = "AIzaSyAQ-e8NgyOHSHBoxSf0OCpJ5Jsxeaw6DYM"
        google_cse_id  = "079228240678147e3"

        os.environ["OPENAI_API_KEY"] = "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"
        os.environ["GOOGLE_CSE_ID"] = google_cse_id
        os.environ["GOOGLE_API_KEY"] = google_api_key
        os.environ["OPENAI_API_KEY"] = "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" # Get it at https://platform.openai.com/account/api-keys

        # llm = ChatOpenAI(temperature=0, model_name="gpt-4", max_tokens=1000)
        # llm = Ollama(model="llama3")
        

        llm = ChatGroq(temperature=0, groq_api_key="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", model_name="llama3-8b-8192") #  "mixtral-8x7b-32768")
        tools = load_tools(["google-search", "human"], llm=llm)

        # import chromadb

        # persistent_client = chromadb.HttpClient(host='95.111.245.169', port=8000) 
        # collection = persistent_client.get_or_create_collection("llama_brain") 

        # create the open-source embedding function
        # embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")


        # langchain_chroma = Chroma(
        #     client=persistent_client,
        #     collection_name="llama_brain",
        #     embedding_function=embedding_function,
        # )
        
        session_id = "FIXED_ID" #uuid.uuid4().hex

        # Initialize SQLChatMessageHistory
        sql_chat_history = SQLChatMessageHistory(
                session_id=session_id, connection_string="sqlite:///chat.db"
        )
        self.sql_chat_history = sql_chat_history

        # Initialize ConversationBufferMemory with SQLChatMessageHistory
        # memory = ConversationBufferMemory(chat_history=sql_chat_history, memory_key="chat_history", return_messages=True)
        memory = ConversationBufferMemory(input_key="input", output_key="output",memory_key="chat_history", return_messages=True)
        self.memory = memory

        # This is where we configure the session id
        config = {"configurable": {"session_id": session_id}}
        self.config = config

        # Initialize the agent
        # db = SQLDatabase.from_uri(f"postgresql+psycopg2://warehouse_user:{DBPASS}@localhost:5432/{DATABASE}")

        # toolkit = SQLDatabaseToolkit(db=db, llm=llm)


        # tools = [add_list, remove_list, save_order_list_tool]

        # tools.append(similarity)

        tools.append(add_product_to_order_list)
        tools.append(product_list)
        tools.append(my_list)
        tools.append(search_product)
        tools.append(remove_product_from_order_list)
        tools.append(save_order_list_tool)


        # tools.append(temp)

        format_instructions_template = """Use the following format:
        Question: the input question you must answer
        Thought: you should always think about what to do
        Action: the action to take, should be one of [{tool_names}]
        Action Input: the input to the action
        Observation: the result of the action
        ... (this Thought/Action/Action Input/Observation can repeat N times)
        Thought: I now know the final answer
        Final Answer: the final answer to the original input question"""

        # structured_llm = llm.with_structured_output(Product)


        # agent_executor = create_sql_agent(
        #     tools=toolkit.get_tools(),
        #     llm=llm,  
        #     toolkit=toolkit,
        #     format_instructions=format_instructions_template,
        #     handle_parsing_errors=True,
        #     verbose=True,
        #     # top_k=20,
        #     agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        #     extra_tools=tools,
        #     suffix=SQL_SUFFIX,
        #     prefix=SQL_PREFIX,
        #     # input_variables=["input", "history", "agent_scratchpad"],
        #     agent_executor_kwargs={
        #         "memory": memory,
        #     },
        # )

        

        # df = pd.read_csv("/home/brunomoya/development/hackupc/seidor-hackupc/api/app/services/products.csv", delimiter=";")

        # llm_bind = llm.bind_tools(tools)

        # agent_executor = create_pandas_dataframe_agent(
        #     llm=llm,
        #     df=df,
        #     include_df_in_prompt=None,
        #     prefix=SQL_PREFIX,
        #     suffix=SQL_SUFFIX,
        #     max_iterations=1,
        #     # format_instructions_template=format_instructions_template,
        #     verbose=True,
        #     agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        #     handle_parsing_errors=True,
        #     input_variables=["input", "agent_scratchpad", "order_list"],
        #     agent_executor_kwargs={
        #         "memory": memory,
        #     },
        #     extra_tools=tools,
        #     # pandas_kwargs={"delimiter": ";"},
        # )

        agent_executor = initialize_agent(
            agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
            tools=tools,
            llm=llm,
            verbose=True,
            max_iterations=1,
            early_stopping_method='generate',
            format_instructions=format_instructions_template,
            memory=memory
        )

        # prompt = PromptTemplate(
        #     template="""You are an agent designed to interact with a .csv file. 
        #     User input will be product names that he wants to order. The agent should return the product ID, name, ean and the quantity available in the warehouse and add it to {order_list}.
        #     If quantity is not specified, ask the user for the quantity.
        #     If the product is not available, the agent should return "Product not available".
        #     If the product is available, but the quantity is less than the requested quantity, the agent should return "Quantity not available".
        #     If the product is available and the quantity is equal to or greater than the requested quantity, the agent should return "Product available".
        #     If the product name is not in the database, the agent should return "Product not found".
        #     Add 5 random products from our list of products in 5 quantities to my order list and then save it
        #     """,
        #     input_variables=["order_list"],
        #     partial_variables={"format_instructions": format_instructions_template})

        # agent_executor.invoke({"input": "Add 5 random products from our list of products in 5 quantities to my order list and then save it", "order_list": order_list}, config=config)
        # result = agent_executor.invoke({"input": "Add 5 random products from our product list in 5 quantities to my order list and then save it", "order_list": order_list}, config=config)
        # result = agent_executor.invoke({"input": "Add me 4 units of 'CALIERCORTIN 4mg/ml- 50ml iny' to my order list", "order_list": order_list}, config=config)
        result = agent_executor.invoke("Add 4 units of 'CALIERCORTIN' to my list and then save it to a .txt file")

        # agent_executor.invoke({"input": "Add 5 random products from our list of products in 5 quantities to my order list and then save it"}, config=config)
        self.table_chain = agent_executor

        # print(result['output'])

        while True:
            query = input("Enter a query: ")
            if query == "exit":
                break
        
            # final_answer = agent.invoke(query, config=config)

            final_answer = agent_executor.invoke({ 
                "input": query, "order_list": order_list}, config=config)
        
            print(final_answer['output'])

            memory.save_context(inputs={"input": query}, outputs={"output": final_answer['output']})

            sql_chat_history.add_user_message(query)
            sql_chat_history.add_ai_message(final_answer['output'])

        # save order_list to a file
        # with open("order_list.txt", "w") as f:
        #     for item in order_list:
        #         f.write("%s\n" % item)


    def text_to_sql(self, text):
        # Use LangChain to convert text to SQL

        final_answer = self.table_chain.invoke({ 
                "input": text, "order_list": order_list}, config=self.config)
        
        print(final_answer['output'])

        self.memory.save_context(inputs={"input": text}, outputs={"output": final_answer['output']})

        self.sql_chat_history.add_user_message(text)
        self.sql_chat_history.add_ai_message(final_answer['output'])

        return final_answer['output']
    
if __name__ == "__main__":
    service = LangChainService()
    # print(service.text_to_sql("Add 5 random products from our list of products in 5 quantities to my order list and then save it"))