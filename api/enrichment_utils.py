from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

template = """You are a university assistant. Rewrite the user query to be clear and unambiguous.
User query: {query}
Rewritten query:"""
prompt = PromptTemplate(template=template, input_variables=["query"])

def clarify_query(query: str) -> str:
    llm = ChatOpenAI(temperature=0)
    chain = LLMChain(llm=llm, prompt=prompt)
    return chain.run(query).strip()
