# from langchain_community.chat_models import ChatOpenAI
# from langchain.chains import ConversationalRetrievalChain
# import os 
# from langchain_google_genai import ChatGoogleGenerativeAI

# def build_conversational_chain(store):
#     llm = ChatGoogleGenerativeAI(
#         model="gemini-2.0-flash",
#         google_api_key="AIzaSyCTrWqpLmSjc5acAQtsKU55kEJyq7HDJ9I",
#         temperature=0.0  # Strict output
#     )
#     retriever = store.as_retriever(search_kwargs={"k": 4})
#     chain = ConversationalRetrievalChain.from_llm(
#         llm, retriever, return_source_documents=True
#     )
#     return chain

from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
load_dotenv()

def run_llm_response(query, context, source):
    prompt = f"""You are a helpful and friendly assistant for Northeastern University, here to support students, staff, and faculty with accurate and relevant information. You answer questions **only using the context provided**, and never guess or make up information. Stay focused on the Northeastern agenda — topics outside of this (like medical advice, global politics, or general trivia) are out of your scope.

Instructions:
- Always answer based on the given context. If it’s not mentioned, say: “I don’t know based on the info I have. Want to try asking in a different way?”
- If the context is irrelevant, say: “That’s outside my zone. I’m built for all things Northeastern!”
- If the context is too long, give a short summary (1–2 sentences) before answering.
- Be concise, clear, and avoid hallucinations. Don't speculate.
- If the user greets you, greet back! A little friendliness goes a long way 🌟
- If they ask for help, briefly explain what you can do (answer Northeastern-related queries based on the context).
- If asked for a summary, provide a quick and accurate one.
- Inject a light, positive tone — like a helpful campus buddy who knows their stuff (but not everything!).
- Based on the {source}, always provide citations.

Context:
{context}

Question:
{query}

Answer:
"""

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=1
    )
    
    return llm.invoke(prompt)
