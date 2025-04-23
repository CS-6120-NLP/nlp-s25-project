from fastapi import APIRouter, HTTPException
from api.pydantic_models import QueryRequest, QueryResponse
from api.auth_utils import get_or_create_session
from api.enrichment_utils import clarify_query
from api.permission_utils import PermissionChecker
# from api.chroma_utils import get_chroma_store
# from api.langchain_utils import build_conversational_chain
from api.persona_utils import filter_by_persona
from api.db_utils import get_db_session
from api.db_models import QueryRecord
from api.chroma_utils import final_retriever
from api.langchain_utils import run_llm_response

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
