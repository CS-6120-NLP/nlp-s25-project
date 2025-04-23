from fastapi import APIRouter

from models.entities import QueryRecord
from models.request_models import QueryRequest
from models.response_models import QueryResponse
from services.chat_service import clarify_query
from services.llm_service import run_llm_response
from services.retrieval_service import final_retriever
from utils.auth_utils import get_or_create_session
# from services.chroma_utils import get_chroma_store
# from services.langchain_utils import build_conversational_chain
from utils.db_utils import get_db_session

router = APIRouter()


@router.post("", response_model=QueryResponse)
def query_endpoint(payload: QueryRequest):
    # Session/auth
    session = get_or_create_session(payload.persona, payload.session_id)

    # Enrich + permission
    clarified = clarify_query(payload.query)
    # checker = PermissionChecker()
    # if not checker.is_permitted(clarified):
    #     raise HTTPException(status_code=403, detail="Query not permitted.")

    # Retrieve + filter
    # store = get_chroma_store()
    # retriever = store.as_retriever(search_kwargs={"k": 5})
    # retriever = filter_by_persona(retriever, payload.persona)
    # docs = retriever.get_relevant_documents(clarified)
    context, source = final_retriever(clarified)

    # Answer
    # chain = build_conversational_chain(store)
    # result = chain({"question": clarified, "chat_history": []})
    # answer = result.get("answer", "")
    # confidence = float(result.get("score", 0.0))
    result = run_llm_response(clarified, context, source)
    answer = result.content if isinstance(result.content, str) else str(result.content)
    confidence = 0.9

    # Persist query record
    db = get_db_session()
    record = QueryRecord(
        session_id=session.id,
        raw_query=payload.query,
        clarified_query=clarified,
        answer=answer,
        confidence=confidence
    )
    db.add(record)
    db.commit()

    return QueryResponse(answer=answer, confidence=confidence)
