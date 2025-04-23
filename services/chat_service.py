from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

from clients.llm_client import get_llm

template = """
You are a query enrichment assistant working for Northeastern University. 
Given the query, enrich it to be clear and unambiguous.

User query: {query}
Rewritten query:

Example:
User Query: What is MS in CS about?
Rewritten Query: What is the Masters in Computer Science about at Northeastern University?

User Query: When is the midterm?
Rewritten Query: What are the midterm examinations at Northeastern University for the current semester?
"""
prompt = PromptTemplate(template=template, input_variables=["query"])


def clarify_query(query: str) -> str:
    llm = get_llm()
    chain = prompt | llm
    return chain.invoke({"query": query}).content.strip()
