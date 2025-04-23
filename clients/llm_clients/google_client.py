from langchain_google_genai import ChatGoogleGenerativeAI

from config import GOOGLE_API_KEY


def get_google_llm(model="gemini-2.0-flash", temperature=0.5):
    return ChatGoogleGenerativeAI(
        model=model,
        google_api_key=GOOGLE_API_KEY,
        temperature=temperature
    )
