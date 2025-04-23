from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

from clients.llm_client import get_llm
from repositories.chat_repository import ChatRepository
from services.llm_service import generate_llm_response
from services.retrieval_service import retrieve_context

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


def clarify_query(query):
    """Clarify and rewrite the user query to be more precise."""
    llm = get_llm()
    chain = prompt | llm
    return chain.invoke({"query": query}).content.strip()


def process_chat(session_id, raw_query):
    # Clarify query
    clarified_query = clarify_query(raw_query)

    # Retrieve context
    context, source = retrieve_context(clarified_query)

    # Generate response
    result = generate_llm_response(clarified_query, context, source)
    answer = result.content if isinstance(result.content, str) else str(result.content)
    confidence = 0.9

    # Save record
    repo = ChatRepository()
    repo.save_chat_record(
        session_id=session_id,
        raw_query=raw_query,
        clarified_query=clarified_query,
        answer=answer,
        confidence=confidence
    )

    return answer, confidence
