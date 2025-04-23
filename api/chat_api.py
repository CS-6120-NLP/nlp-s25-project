from fastapi import APIRouter

from models.entities import QueryRecord
from models.request_models import QueryRequest
from models.response_models import QueryResponse
from services.chat_service import clarify_query
from services.llm_service import generate_llm_response
from services.retrieval_service import retrieve_context
from utils.authentication import get_or_create_session
from utils.database import get_db_session

router = APIRouter()


@router.post("", response_model=QueryResponse)
def query_endpoint(payload: QueryRequest):
    # Initialize session
    session = get_or_create_session(payload.persona, payload.session_id)

    # Clarify query
    clarified_query = clarify_query(payload.query)
    context, source = retrieve_context(clarified_query)

    # Answer
    result = generate_llm_response(clarified_query, context, source)
    answer = result.content if isinstance(result.content, str) else str(result.content)
    confidence = 0.9

    # Persist query record
    db = get_db_session()
    record = QueryRecord(
        session_id=session.id,
        raw_query=payload.query,
        clarified_query=clarified_query,
        answer=answer,
        confidence=confidence
    )
    db.add(record)
    db.commit()

    return QueryResponse(answer=answer, confidence=confidence)
