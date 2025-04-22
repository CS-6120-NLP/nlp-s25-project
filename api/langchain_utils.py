from langchain_community.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain

def build_conversational_chain(store):
    llm = ChatOpenAI(temperature=0)
    retriever = store.as_retriever(search_kwargs={"k": 4})
    chain = ConversationalRetrievalChain.from_llm(
        llm, retriever, return_source_documents=True
    )
    return chain
