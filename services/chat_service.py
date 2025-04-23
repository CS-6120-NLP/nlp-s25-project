from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

from clients.llm_client import get_llm
from repositories.chat_repository import ChatRepository
from services.llm_service import generate_llm_response
from services.retrieval_service import retrieve_context
from utils.authentication import get_or_create_session
from utils.database import get_chat_history

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

Chat History:
{chat_history}
"""
prompt = PromptTemplate(template=template, input_variables=["query"])


def clarify_query(query, chat_history):
    """Clarify and rewrite the user query to be more precise."""
    llm = get_llm()
    chain = prompt | llm

    formatted_history = "\n".join(
        f"{message['role'].capitalize()}: {message['content']}" for message in chat_history
    )

    return chain.invoke({"query": query, "chat_history": formatted_history}).content.strip()


def process_chat(session_id, raw_query, session):
    # Retrieve chat history
    chat_history = [{"role": msg.role, "content": msg.content} for msg in get_chat_history(session.id)]

    # Clarify query
    clarified_query = clarify_query(raw_query, chat_history)

    # Retrieve context
    context, source = retrieve_context(clarified_query)

    # Generate response
    result = generate_llm_response(clarified_query, context, source, chat_history)
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
