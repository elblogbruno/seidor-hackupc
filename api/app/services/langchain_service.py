from langchain.agents import AgentType, initialize_agent, load_tools, create_react_agent, AgentExecutor
import os
 
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


from langchain.agents import create_sql_agent 
from langchain.agents.agent_toolkits import SQLDatabaseToolkit 
from langchain.agents.agent_types import AgentType
from tools.dht11 import get_dht11_data

DBPASS = "test"
DATABASE = "warehouse"

SQL_PREFIX = """You are an agent designed to interact with a SQL database.
Given an input question, create a syntactically correct {dialect} query to run, then look at the results of the query and return the answer.
Always limit your query to at most {top_k} results using the LIMIT clause.
You can order the results by a relevant column to return the most interesting examples in the database.
Never query for all the columns from a specific table, only ask for a the few relevant columns given the question.
If you get a "no such table" error, rewrite your query by using the table in quotes.
DO NOT use a column name that does not exist in the table.
You have access to tools for interacting with the database.
Only use the below tools. Only use the information returned by the below tools to construct your final answer.
You MUST double check your query before executing it. If you get an error while executing a query, rewrite a different query and try again.
DO NOT try to execute the query more than three times.
DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.
If the question does not seem related to the database, just return "I don't know" as the answer.
If you cannot find a way to answer the question, just return the best answer you can find after trying at least three times.
You can also use the internet to find the answer to the question using the "google-search" tool.
""";


SQL_SUFFIX = """Begin!
Question: {input}
Thought: I should look at the tables in the database to see what I can query.
{agent_scratchpad}"""

class LangChainService:
    def __init__(self):
        google_api_key = "AIzaSyAQ-e8NgyOHSHBoxSf0OCpJ5Jsxeaw6DYM"
        google_cse_id  = "079228240678147e3"

        # os.environ["OPENAI_API_KEY"] = "[INSERT YOUR OPENAI API KEY HERE]"
        os.environ["GOOGLE_CSE_ID"] = google_cse_id
        os.environ["GOOGLE_API_KEY"] = google_api_key
        os.environ["OPENAI_API_KEY"] = "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" # Get it at https://platform.openai.com/account/api-keys

        # llm = OpenAI(temperature=0, base_url="http://localhost:1234/v1", api_key="not-needed")
        # llm = OpenAI(temperature=0)

        llm = ChatGroq(temperature=0, groq_api_key="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", model_name="mixtral-8x7b-32768")
        tools = load_tools(["google-search"], llm=llm)

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

        # Initialize ConversationBufferMemory with SQLChatMessageHistory
        # memory = ConversationBufferMemory(chat_history=sql_chat_history, memory_key="chat_history", return_messages=True)
        memory = ConversationBufferMemory(chat_history=sql_chat_history, memory_key="chat_history", return_messages=True)
        

        # This is where we configure the session id
        config = {"configurable": {"session_id": session_id}}

        # Initialize the agent
        db = SQLDatabase.from_uri(f"postgresql+psycopg2://warehouse_user:{DBPASS}@localhost:5432/{DATABASE}")

        toolkit = SQLDatabaseToolkit(db=db, llm=llm)

        tools.append(get_dht11_data)

        format_instructions_template = """Use the following format:

        Question: the input question you must answer
        Thought: you should always think about what to do
        Action: the action to take, should be one of [{tool_names}]
        Action Input: the input to the action
        Observation: the result of the action
        ... (this Thought/Action/Action Input/Observation can repeat N times)
        Thought: I now know the final answer
        Final Answer: the final answer to the original input question"""

        agent_executor = create_sql_agent(
            tools=toolkit.get_tools(),
            llm=llm,  
            toolkit=toolkit,
            format_instructions=format_instructions_template,
            handle_parsing_errors=True,
            verbose=True,
            top_k=20,
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            extra_tools=tools,
            suffix=SQL_SUFFIX,
            prefix=SQL_PREFIX,
        )

        agent_executor.run("Show me all the tables in the database")
        agent_executor.run("Who is rubiales? Search the internet for me and then save the answer in the database")

        self.table_chain = agent_executor

    def text_to_sql(self, text):
        # Use LangChain to convert text to SQL
        result = self.table_chain.invoke(text)

        return result