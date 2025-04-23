import cohere

from config import COHERE_API_KEY


def get_cohere_client():
    return cohere.ClientV2(api_key=COHERE_API_KEY)


def rerank_documents(query, documents, model='rerank-english-v2.0', top_n=5):
    client = get_cohere_client()
    return client.rerank(
        model=model,
        query=query,
        documents=documents,
        top_n=top_n
    )
