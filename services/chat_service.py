import re

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

from clients.llm_client import get_llm, generate_chat_response
from config import PERMISSION_THRESHOLD
from repositories.chat_repository import ChatRepository
from services import session_service
from services.retrieval_service import retrieve_context
from services.session_service import get_session_summary, get_session

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

Previous Chat Summary:
{chat_summary}
"""
prompt = PromptTemplate(template=template, input_variables=["query"])


def clarify_query(query, chat_summary):
    """Clarify and rewrite the user query to be more precise."""
    llm = get_llm()

    input_text = prompt.format(query=query, chat_summary=chat_summary)
    return llm.invoke(input_text).content.strip()


def get_chat_history(session_id):
    """Retrieve chat history from the database."""
    repo = ChatRepository()
    return repo.get_chat_history(session_id)


def process_chat(session_id, persona, raw_query):
    # Validate session. If it doesn't exist, create a new one.
    session = get_session(session_id, persona)

    chat_summary = get_session_summary(session.session_id)

    # Clarify query
    clarified_query = clarify_query(raw_query, chat_summary)

    # Retrieve context
    context, source = retrieve_context(clarified_query)

    # Generate response
    result = generate_chat_response(clarified_query, context, source, chat_summary)
    answer = result.content if isinstance(result.content, str) else str(result.content)
    confidence_match = re.search(r"\[Confidence:\s*([0-9]*\.?[0-9]+)]", answer)
    confidence = float(confidence_match.group(1)) if confidence_match else None

    # Low confidence handling
    if confidence is None or confidence < PERMISSION_THRESHOLD:
        answer = "I'm not sure about that. Can you please rephrase your question or provide more details?"
        confidence = 0.0

    # Save record
    repo = ChatRepository()
    saved_chat_record = repo.save_chat_record(
        session_id=session.id,
        raw_query=raw_query,
        clarified_query=clarified_query,
        answer=answer,
        confidence=confidence
    )

    # Update session summary
    session_service.update_session_summary(session.id, chat_summary, saved_chat_record)

    return answer, confidence
