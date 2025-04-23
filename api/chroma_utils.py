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
    return results['documents'][0], results['metadatas'][0]

def retriever2_semantic(query: str):
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    collection2 = chroma_client.get_collection(name="semantic_cluster")
    results = collection2.query(
        query_texts=[query],
        n_results=10
    )
    # print(results)
    return results['documents'][0], results['metadatas'][0]

def retriever3_page_chunks(query: str):
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    collection3 = chroma_client.get_collection(name="page_chunks")
    results = collection3.query(
        query_texts=[query],
        n_results=5
    )
    # print(results)
    return results['documents'][0], results['metadatas'][0]

def retriever4_hyde(query: str):    
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    k=10
    def HydeRagSystem(model_name, query):
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=os.getenv("GOOGLE_API_KEY"),  # safer than hardcoding
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
    return retrieved_docs['documents'][0], retrieved_docs['metadatas'][0], hyde_doc

def hybrid_query_model(query):
    retr1, meta1 = retriever1_manual(query)
    retr2, meta2 = retriever2_semantic(query)
    retr3, meta3 = retriever3_page_chunks(query)
    retr4, meta4, hyde_doc = retriever4_hyde(query)

    combined_docs = retr1 + retr2 + retr3 + retr4
    combined_meta = meta1 + meta2 + meta3 + meta4
    doc_meta_pairs = list(zip(combined_docs, combined_meta))

    seen = set()
    unique_doc_meta_pairs = []
    for doc, meta in doc_meta_pairs:
        if doc not in seen:
            unique_doc_meta_pairs.append((doc, meta))
            seen.add(doc)

    unique_docs = [doc for doc, _ in unique_doc_meta_pairs]

    #Re-ranker
    cohere_api_key = os.getenv("COHERE_API_KEY")
    import cohere
    co = cohere.ClientV2(api_key=cohere_api_key)
    result = co.rerank(model='rerank-english-v2.0', query=query, documents=unique_docs, top_n=5)
    reranked = []
    for res in result.results:
        doc, meta = unique_doc_meta_pairs[res.index]
        url = meta.get("url", "No URL") if meta else "No Metadata"
        reranked.append((doc, url))
    return reranked


def final_retriever(query):
    docs_url = hybrid_query_model(query)
    context = "\n\n".join([doc for doc, url in docs_url if doc])
    source = [url for doc, url in docs_url]
    return context, source
