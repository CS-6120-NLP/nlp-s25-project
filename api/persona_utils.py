def filter_by_persona(retriever, persona: str):
    original = retriever.get_relevant_documents
    def filtered(query):
        docs = original(query)
        return [d for d in docs if persona in d.metadata.get('persona_tags', [])]
    retriever.get_relevant_documents = filtered
    return retriever
