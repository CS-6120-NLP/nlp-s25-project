from fastapi import APIRouter, HTTPException
from torch.distributed.tensor import empty
from unstructured_client.types import Nullable

from api.pydantic_models import QueryRequest, QueryResponse
from api.auth_utils import get_or_create_session
from api.enrichment_utils import clarify_query
from api.permission_utils import PermissionChecker
from api.chroma_utils import get_chroma_store
from api.langchain_utils import build_conversational_chain
from api.persona_utils import filter_by_persona
from api.db_utils import get_db_session
from api.db_models import QueryRecord, UserSession
from config.default_settings import CHAT_HISTORY_WINDOW

import openai
import json


router = APIRouter()


@router.post("", response_model=QueryResponse)
def query_endpoint(payload: QueryRequest):
    # Session/auth
    session = get_or_create_session(payload.persona, payload.session_id)

    # Enrich + permission
    clarified = clarify_query(payload.query)
    checker = PermissionChecker()
    if not checker.is_permitted(clarified):
        raise HTTPException(status_code=403, detail="Query not permitted.")

    # Retrieve + filter
    store = get_chroma_store()
    # retriever = store.as_retriever(search_kwargs={"k": 5})
    # retriever = filter_by_persona(retriever, payload.persona)
    # docs = retriever.get_relevant_documents(clarified)

    # Answer
    db = get_db_session()
    chain = build_conversational_chain(store)
    chat_hist = get_chat_history(db, session.id)
    result = chain({"question": clarified, "chat_history": chat_hist})
    answer = result.get("answer", "")
    confidence = float(result.get("score", 0.0))

    # Persist query record
    record = QueryRecord(
        session_id=session.id,
        raw_query=payload.query,
        clarified_query=clarified,
        answer=answer,
        confidence=confidence
    )

    chat_hist_summary = get_chat_summary(db,payload.session_id, record.raw_query)
    db.add(record)
    db.commit()

    # return QueryResponse(answer=answer, confidence=confidence)
    return QueryResponse(answer="test1", confidence=90)


def get_chat_history(db, session_id, limit=CHAT_HISTORY_WINDOW):
    """
    Retrieve the 40 latest chat history records from the database for a given session_id.
    """
    records = (db.query(QueryRecord).
              filter(QueryRecord.session_id == session_id).
              order_by(QueryRecord.timestamp.desc()).
              limit(limit).all())
    return [(r.raw_query, r.answer) for r in records]


def get_chat_summary(db,session_id, latest_message):
    """
    New summary = old chat summary + latest chat message
    latest_message : raw query from this asking
    """

    # get UserSession Info
    session = db.query(UserSession).filter_by(session_id=session_id).first()
    if session is None :
        print("Did not find this user = ", {session_id})
        return ""

    prompt ="""
        Use the chat summary and latest message to generate new summary for the user. 
    """

    # Todo !!! Change Open AI to the Gemini(Free)
    new_summary = generate_chat_summary_with_openai(session.chat_summary, json.dumps(latest_message,default= str))

    # adding the new summary to the userSession
    session.chat_summary = new_summary
    db.commit()
    return new_summary


def generate_chat_summary_with_openai(chat_summary, latest_message):
    """
    Generate a new chat summary using OpenAI's API.
    """
    messages = [
        {"role": "system", "content": "You are a helpful assistant that summarizes chat history."},
        {"role": "user", "content": f"Previous chat summary: {chat_summary}"},
        {"role": "user", "content": f"Latest message: {latest_message}"},
        {"role": "user", "content": "Generate a new concise chat summary that incorporates the latest message."}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # You can use other models like "gpt-3.5-turbo"
        messages=messages,
        max_tokens=100,  # Adjust based on your needs
        temperature=0.5  # Adjust for creativity vs. consistency
    )

    return response.choices[0].message["content"].strip()
