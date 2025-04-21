import os
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from config.default_settings import PERMISSION_THRESHOLD

class PermissionChecker:
    def __init__(self):
        embeddings = OpenAIEmbeddings()
        self.unpermitted_store = Chroma(
            persist_directory='permission_unpermitted/',
            embedding_function=embeddings
        )
        self.threshold = PERMISSION_THRESHOLD

    def is_permitted(self, query: str) -> bool:
        scores = self.unpermitted_store.similarity_search_with_score(query, k=1)
        if scores and scores[0][1] > self.threshold:
            return False
        return True
