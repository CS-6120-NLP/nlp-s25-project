from utils.retriever import Retriever

retriever = Retriever()


def retrieve_context(query: str):
    return retriever.retrieve(query)
