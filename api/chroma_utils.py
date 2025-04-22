# import os
# from langchain_community.embeddings import OpenAIEmbeddings
# from langchain_community.vectorstores import Chroma

# def get_chroma_store(persist_directory="chroma_db"):
#     embeddings = OpenAIEmbeddings()
#     os.makedirs(persist_directory, exist_ok=True)
#     store = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
#     return store


import chromadb
import os
from dotenv import load_dotenv
import chromadb
import os
from chromadb.utils import embedding_functions
import chromadb
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import HuggingFaceEndpoint
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.llms import Ollama
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
load_dotenv()

def retriever1_manual(query: str):
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    collection = chroma_client.get_collection(name="manual_catalog")
    results = collection.query(
        query_texts=[query],
        n_results=10
    )

    # print(results)
    return results['documents']

def retriever2_semantic(query: str):
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    collection2 = chroma_client.get_collection(name="semantic_cluster")
    results = collection2.query(
        query_texts=[query],
        n_results=10
    )
    # print(results)
    return results['documents']

def retriever3_page_chunks(query: str):
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    collection3 = chroma_client.get_collection(name="page_chunks")
    results = collection3.query(
        query_texts=[query],
        n_results=5
    )
    # print(results)
    return results['documents']

def retriever4_hyde(query: str):    
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    k=10
    def HydeRagSystem(model_name, query):
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=1
        )

        hyde_prompt = PromptTemplate.from_template(
                """You are an expert knowledge base assistant. Based on the user query, 
                generate a detailed hypothetical document that would be the perfect 
                response to this query. This hypothetical document will be used to 
                retrieve relevant actual documents from a knowledge base.
                
                User Query: {query}
                
                Hypothetical Document:"""
            )
        chain = hyde_prompt | llm | StrOutputParser()
        hyde_doc = chain.invoke({"query": query})
        return hyde_doc
    
    hyde_doc = HydeRagSystem("google/flan-t5-base", query)
    collection3 = chroma_client.get_collection(name="page_chunks")
    retrieved_docs = collection3.query(query_texts=[hyde_doc], n_results=k)
    return retrieved_docs['documents'], hyde_doc

def hybrid_query_model(query):
    retr1 = retriever1_manual(query)
    retr2 = retriever2_semantic(query)
    retr3 = retriever3_page_chunks(query)
    retr4, hyde_doc = retriever4_hyde(query)
    #Re-ranker

    import cohere
    co = cohere.ClientV2(api_key=os.getenv("COHERE_API_KEY"))
    overall_documents=retr1[0] + retr2[0] + retr3[0] + retr4[0]
    overall_documents = list(set(overall_documents))
    result = co.rerank(model='rerank-english-v2.0', query=query, documents=overall_documents, top_n=5)
    reranked_docs = [overall_documents[ele.index] for ele in result.results]
    return reranked_docs


def final_retriever(query):
    docs = hybrid_query_model(query)
    context = "\n\n".join([doc for doc in docs if doc])
    return context
