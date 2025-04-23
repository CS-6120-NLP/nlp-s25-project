from typing import Set

import chromadb
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from clients.cohere_client import rerank_documents
from clients.llm_client import get_llm


class Retriever:
    def __init__(self, db_path="data/chroma_db"):
        self.chroma_client = chromadb.PersistentClient(path=db_path)

    def retrieve_from_manual_catalog(self, query, n_results=10):
        collection = self.chroma_client.get_collection(name="manual_catalog")
        results = collection.query(query_texts=[query], n_results=n_results)
        return results['documents'][0], results['metadatas'][0]

    def retrieve_from_semantic_cluster(self, query, n_results=10):
        collection = self.chroma_client.get_collection(name="semantic_cluster")
        results = collection.query(query_texts=[query], n_results=n_results)
        return results['documents'][0], results['metadatas'][0]

    def retrieve_from_page_chunks(self, query, n_results=5):
        collection = self.chroma_client.get_collection(name="page_chunks")
        results = collection.query(query_texts=[query], n_results=n_results)
        return results['documents'][0], results['metadatas'][0]

    def retrieve_with_hyde(self, query, n_results=10):
        llm = get_llm()
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

        # Use hypothetical document to retrieve
        collection = self.chroma_client.get_collection(name="page_chunks")
        retrieved_docs = collection.query(query_texts=[hyde_doc], n_results=n_results)
        return retrieved_docs['documents'][0], retrieved_docs['metadatas'][0], hyde_doc

    def hybrid_retrieval(self, query):
        docs1, meta1 = self.retrieve_from_manual_catalog(query)
        docs2, meta2 = self.retrieve_from_semantic_cluster(query)
        docs3, meta3 = self.retrieve_from_page_chunks(query)
        docs4, meta4, _ = self.retrieve_with_hyde(query)

        # Combine and deduplicate results
        combined_docs = docs1 + docs2 + docs3 + docs4
        combined_meta = meta1 + meta2 + meta3 + meta4
        doc_meta_pairs = list(zip(combined_docs, combined_meta))

        seen: Set[str] = set()
        unique_doc_meta_pairs = []

        for doc, meta in doc_meta_pairs:
            if doc not in seen:
                unique_doc_meta_pairs.append((doc, meta))
                seen.add(doc)

        unique_docs = [doc for doc, _ in unique_doc_meta_pairs]

        # Rerank results
        result = rerank_documents(query=query, documents=unique_docs, top_n=5)
        reranked = []

        for res in result.results:
            doc, meta = unique_doc_meta_pairs[res.index]
            url = meta.get("url", "No URL") if meta else "No Metadata"
            reranked.append((doc, url))

        return reranked

    def retrieve(self, query):
        docs_url = self.hybrid_retrieval(query)
        context = "\n\n".join([doc for doc, url in docs_url if doc])
        sources = [url for doc, url in docs_url]
        return context, sources
