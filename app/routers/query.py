from fastapi import APIRouter, HTTPException
from api.pydantic_models import QueryRequest, QueryResponse
from api.auth_utils import get_or_create_session
from api.enrichment_utils import clarify_query
from api.permission_utils import PermissionChecker
# from api.chroma_utils import get_chroma_store
# from api.langchain_utils import build_conversational_chain
from api.persona_utils import filter_by_persona
from api.db_utils import get_db_session, get_chat_history, save_chat_message, save_query_record
from api.db_models import QueryRecord
from api.chroma_utils import final_retriever
from api.langchain_utils import run_llm_response

router = APIRouter()

@router.post("", response_model=QueryResponse)
def query_endpoint(payload: QueryRequest):
    # Session/auth
    session = get_or_create_session(payload.persona, payload.session_id)

    # Retrieve chat history
    chat_history = [{"role": msg.role, "content": msg.content} for msg in get_chat_history(session.id)]

    # Enrich + permission
    clarified = clarify_query(payload.query)

    # Retrieve + filter
    context, source = final_retriever(clarified)

    # Answer with chat history
    result = run_llm_response(clarified, context, source, chat_history)
    answer = result.content if isinstance(result.content, str) else str(result.content)
    confidence = 0.9

    # Persistent record
    save_query_record(session.id, payload.query, clarified, answer, confidence)
    save_chat_message(session.id, "user", payload.query)
    save_chat_message(session.id, "assistant", answer)

    return QueryResponse(answer=answer, confidence=confidence)
