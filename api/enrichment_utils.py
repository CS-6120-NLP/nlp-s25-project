from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
load_dotenv()

template = """
You are a query enrichment assistant. Given the query erich it to be clear and unambiguous.
User query: {query}
Rewritten query:

Example:
User query: What is MS in CS about?
Rewritten query: What is the Masters in Computer Science about?

"""
prompt = PromptTemplate(template=template, input_variables=["query"])

def clarify_query(query: str) -> str:
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.5  # Strict output
    )
    chain = LLMChain(llm=llm, prompt=prompt)
    return chain.run(query).strip()
