import pandas as pd

from langchain.document_loaders import DataFrameLoader
from langchain.llms import OpenAI
from langchain.embeddings.huggingface  import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_community.llms import Ollama


df = pd.read_csv('products.csv', sep=';')

loader = DataFrameLoader(df, page_content_column="name")
docs = loader.load()

embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")
vectorstore = Chroma.from_documents(docs, embeddings)

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

llm = Ollama(model="mistral")

qa = ConversationalRetrievalChain.from_llm(
    llm, 
    vectorstore.as_retriever(search_kwargs={"k": 3}),
    memory=memory
)

q_1 = "What are all of the document titles?"
result = qa({"question": q_1})