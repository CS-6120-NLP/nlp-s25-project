import re

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

from clients.llm_client import get_llm
from config import PERMISSION_THRESHOLD
from repositories.chat_repository import ChatRepository
from repositories.session_repository import SessionRepository
from services.llm_service import generate_llm_response, generate_updated_summary
from services.retrieval_service import retrieve_context
from services.session_service import get_summary

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


def process_chat(session_id, raw_query):
    prev_summary = get_summary(session_id)
    if prev_summary is None:
        prev_summary = ""

        # Retrieve chat history
        chat_history = [{"raw_query": chat_record.raw_query, "clarified_query": chat_record.clarified_query,
                         "answer": chat_record.answer} for chat_record in get_chat_history(session_id)]

        for record in chat_history:
            prev_summary += f"- User: {record['raw_query']}\n- AI: {record['answer']}\n"

    # Clarify query
    clarified_query = clarify_query(raw_query, prev_summary)

    # Retrieve context
    context, source = retrieve_context(clarified_query)

    # Generate response
    result = generate_llm_response(clarified_query, context, source, prev_summary)
    answer = result.content if isinstance(result.content, str) else str(result.content)
    confidence_match = re.search(r"\[Confidence:\s*([0-9]*\.?[0-9]+)]", answer)
    confidence = float(confidence_match.group(1)) if confidence_match else None

    # Low confidence handling
    if confidence is None or confidence < PERMISSION_THRESHOLD:
        answer = "I'm not sure about that. Can you please rephrase your question or provide more details?"
        confidence = 0.0

    # Update chat summary
    updated_summary = generate_updated_summary(prev_summary, {"raw_query": raw_query, "answer": answer})

    # Save record
    ChatRepository().save_chat_record(
        session_id=session_id,
        raw_query=raw_query,
        clarified_query=clarified_query,
        answer=answer,
        confidence=confidence
    )
    SessionRepository().save_summary(
        session_id=session_id,
        summary=updated_summary
    )

    return answer, confidence
