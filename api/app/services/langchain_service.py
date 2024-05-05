from typing import List, Optional, Union
from langchain.agents import AgentType, initialize_agent, load_tools, create_react_agent, AgentExecutor
import os

from langchain_openai import OpenAI, ChatOpenAI
from langchain_groq import ChatGroq


from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import PromptTemplate 
from langchain_community.chat_message_histories import SQLChatMessageHistory

from langchain_core.pydantic_v1 import BaseModel, Field


# from langchain.agents import create_sql_agent 
from langchain.agents.agent_types import AgentType
# from tools.dht11 import get_Dht11
from langchain.tools import BaseTool, StructuredTool, tool

# from langchain.tools.base import StructuredTool

# from langchain_experimental.agents.agent_toolkits import create_csv_agent, create_pandas_dataframe_agent

import pandas as pd

from langchain_core.pydantic_v1 import BaseModel, Field
from fuzzywuzzy import fuzz

from langchain_community.llms import Ollama

google_api_key = "AIzaSyAQ-e8NgyOHSHBoxSf0OCpJ5Jsxeaw6DYM"
google_cse_id  = "079228240678147e3"

os.environ["OPENAI_API_KEY"] = "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"
os.environ["GOOGLE_CSE_ID"] = google_cse_id
os.environ["GOOGLE_API_KEY"] = google_api_key
os.environ["OPENAI_API_KEY"] = "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" # Get it at https://platform.openai.com/account/api-keys


class Product(BaseModel):
    id: Optional[Union[str, int]] = Field(description="The product ID")
    name: str = Field(description="The product name")
    ean: Optional[Union[str, int]] = Field(description="The product EAN")
    quantity: Optional[int] = Field(description="The quantity available in the warehouse")


class Order(BaseModel):
    """Extracted data about people."""

    # Creates a model so that we can extract multiple entities.
    products: List[Product]


# TODO:  SEE IF WE CAN SPEAK IN OTHER LANGUAGES

SQL_PREFIX = """
First conversation with the user always ask for the language to be used during the conversation. If user does not specify, use English. 
if user specifies a language, use that language for the rest of the conversation.
You are an agent designed to interact with a .csv file to help an user order products from a warehouse.
{input} will be a product name that he wants to order from the .csv file. 
The agent should get the product ID, name, ean from .csv and add it to {order_list}.
If product is not found, search the product name that highly matches the user input in the .csv file. If found, add the product to  {order_list}.
If multiple products are found, let the user choose one by letting him select the correct product Name.
If product is not found, let the user know that the product is not found.
Only add one product to the order list at a time.
If quantity is not specified, ask the user for the quantity. If quantity is specified, add the product to the order list with the specified quantity.
User can also ask to remove a product from the order list or reduce the quantity of a product in the order list. 
User can also ask to save the order list to a file, that is confirm the order and send to the warehouse.
Always show the current order list to the user.

If you are unsure of the next step, show your output and ask user for input.
Do not role play in the conversation. For example, generating AI and Human conversation is not allowed.
"""
# Always ask the user for the next step.

# Always answer returning {order_list} at the end of the answer.


SQL_SUFFIX = """Begin!
history: {chat_history}
order_list: {order_list}
Question: {input}
Thought: You should always think about what to do
{agent_scratchpad}"""

order_list = []


import json


@tool("add_product_to_order_list")
def add_product_to_order_list(name: str, quantity: int = 1) -> str:
    """Add a product to the order list."""
    # Add a product to the order list
    products = search_products(name)

    if len(products) == 0:
        return "Product not found"
    
    if len(products) > 1:
        return "Multiple products found. Let the user choose one. " + str(products)

    product = products[0]

    if product is None:
        return "Product not found"
    
    product["quantity"] = quantity

    global order_list

    print("Adding product to order list: ", product)

    order_list.append(product)

    return my_order()


@tool()
def product_list(query: str = "") -> str:
    """Get the list of products."""
    # TODO: Get from INTERNET (MY VPS OR SOMETHING, AND WE CAN ALWAYS GRAB LATEST DATA) 
    # IN CASE OF WAREHOUSE WE WILL HAVE SOME CSV LIKE THIS BUT WITH MORE DATA (LOCATION + TEMPERATURE ETC.)
    # path = "/home/brunomoya/development/hackupc/seidor-hackupc/api/app/services/products.csv"
    print("Getting the list of products from main server")
    path = "http://95.111.245.169:8000/client/"

    df = pd.read_csv(path, delimiter=";")

    if query:
        print("Querying for: ", query)
        df = df[df["name"].str.contains(query, case=False, na=False)]
        return df.to_json(orient="records")
    
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

@tool("show_order_list")
def my_order() -> str:
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
def search_products(product_name: str) -> List[Product]:
    """Search for a product in the product list."""
    path = "http://95.111.245.169:8000/client/"
    df = pd.read_csv(path, delimiter=";")
    products = df[df["name"].str.contains(product_name, case=False, na=False)].to_dict(orient="records")
    
    return products

@tool()
def search_products_by_id(id: str) -> List[Product]:
    """Search for a product in the product list."""
    path = "http://95.111.245.169:8000/client/"
    df = pd.read_csv(path, delimiter=";")
    products = df[df["id"] == id].to_dict(orient="records")
    
    return products

@tool("similarity", args_schema=Product, return_direct=True)
def similarity(user_input_name: str, product_name: str) -> float:
    """Check the similarity between two strings."""
    # Check the similarity between two strings
    return fuzz.token_sort_ratio(user_input_name, product_name)

@tool()
def remove_product_from_order_list(id: str) -> List[Product]:
    """Remove a product from the order list."""
    global order_list
    # Remove a product from the order list
    order_list_filtered = [item for item in order_list if item["id"] != id]
    return order_list_filtered

@tool()
def confirm_order(order_list: List[Product]) -> str:
    # SAVE TO INTERNET VPS SO THE WAREHOUSE WORKER HAS ACCESS TO IT AND ITS AI LEARS FROM IT.
    """Confirm the order."""
    print("Saving order list to a file")
    
    import requests


    print(order_list)

    # do a POST request to the server (PI IOT DEVICE) with the order list
    path = "http://192.168.124.15:8000/save_order/"

    try:
        order = Order(products=order_list)

        # do a post request to the server with the order list
        response = requests.post(path, json=order.dict())

        if response.status_code == 200:
            return "Order confirmed"
    except Exception as e:
        return f"Error saving order: {e}"
    
    return "Error saving order: " + response.text



def get_input() -> str:
    print("Insert your text. Enter 'q' or press Ctrl-D (or Ctrl-Z on Windows) to end.")
    contents = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line == "q":
            break
        contents.append(line)
    return "\n".join(contents)

class LangChainService:
    def __init__(self, on_human_input=None, cli_mode=False):

        llm = ChatOpenAI(temperature=0)
        # llm = Ollama(model="mistral")
        # llm = ChatGroq(temperature=0, groq_api_key="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", model_name="mixtral-8x7b-32768") #"llama3-8b-8192") #  "mixtral-8x7b-32768")
        
        tools = load_tools(["google-search", "human"], llm=llm, input_func=on_human_input)
        
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


        tools.append(add_product_to_order_list)
        tools.append(product_list)
        tools.append(my_order)
        # tools.append(search_product)
        tools.append(search_products)
        tools.append(remove_product_from_order_list)
        tools.append(confirm_order)


        # tools.append(temp)

        format_instructions_template = """Use the following format:
        Question: the input question you must answer
        Thought: you should always think about what to do
        Action: the action to take, should be one of [{tool_names}]
        Action Input: the input to the action
        Observation: the result of the action
        ... (this Thought/Action/Action Input/Observation can repeat N times)
        Thought: I now know the final answer
        Final Answer: the final answer to the original input question
        """
        
        FORMAT_INSTRUCTIONS = """To use a tool, please use the following format:
        '''
        Thought: Do I need to use a tool? Yes
        Action: the action to take, should be one of [{tool_names}]
        Action Input: the input to the action
        Observation: the result of the action
        '''

        When you have gathered all the information regarding AI algorithm, just write it to the user in the form of a blog post.

        '''
        Thought: Do I need to use a tool? No
        AI: the final answer to the original input question
        '''
        """

        agent_executor = initialize_agent(
            agent=AgentType.OPENAI_FUNCTIONS,
            tools=tools,
            llm=llm,
            verbose=True,
            max_iterations=1,
            early_stopping_method='generate',
            memory=memory,
            input_variables=["input", "agent_scratchpad", "order_list", "chat_history"],
            return_intermediate_steps=True,
            agent_kwargs={
                "prefix": SQL_PREFIX,
                # "format_instructions": format_instructions_template,
                "format_instructions":format_instructions_template,

                "suffix": SQL_SUFFIX,
            },
        )

        # result = agent_executor.invoke("Add 4 units of 'CALIERCORTIN' to my list and then save it to a .txt file")

        # agent_executor.invoke({"input": "Add 5 random products from our list of products in 5 quantities to my order list and then save it"}, config=config)
        self.table_chain = agent_executor

        # make the agent ask the user for language input at the beginning of the conversation
        # result = agent_executor.invoke({"input": "human what language should I speak during our conversation?", "order_list": order_list}, config=config)


        # print(result['output'])
        if cli_mode:
            while True:
                query = input("Enter a query: ")
                if query == "exit":
                    break
            
                # final_answer = agent.invoke(query, config=config)

                final_answer = agent_executor.invoke({ 
                    "input": query, "order_list": order_list, "chat_history": sql_chat_history.messages}, config=config)
            
                print(final_answer['output'])

                memory.save_context(inputs={"input": query}, outputs={"output": final_answer['output'], "order_list": order_list}) #, "chat_history": sql_chat_history.messages})

                sql_chat_history.add_user_message(query)
                sql_chat_history.add_ai_message(final_answer['output'])

            # save order_list to a file
            with open("order_list.txt", "w") as f:
                for item in order_list:
                    f.write("%s\n" % item)


    def text_to_sql(self, text):
        # Use LangChain to convert text to SQL
        final_answer = self.table_chain.invoke({ 
                "input": text, "order_list": order_list, "chat_history": self.sql_chat_history.messages}, config=self.config)
        
        print("OUTPUT: " + str(final_answer['output']))

        self.memory.save_context(inputs={"input": text}, outputs={"output": final_answer['output'], "order_list": order_list})

        self.sql_chat_history.add_user_message(text)
        self.sql_chat_history.add_ai_message(final_answer['output'])

        return final_answer['output']
    
    def initial_poke(self):
        result = self.table_chain.invoke({"input": "Hello Fellow Human! What language should I speak during our conversation?", "order_list": order_list}, config=self.config)

        return result['output']
    
if __name__ == "__main__":
    service = LangChainService(on_human_input=get_input, cli_mode=True)