import os
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

def get_chroma_store(persist_directory="chroma_db"):
    embeddings = OpenAIEmbeddings()
    os.makedirs(persist_directory, exist_ok=True)
    store = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
    return store
