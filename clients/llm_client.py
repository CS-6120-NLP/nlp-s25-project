from clients.llm_clients.google_client import get_google_llm
from config import LLM_PROVIDER, GOOGLE_LLM_MODEL, GOOGLE_LLM_BASE_MODEL


def get_llm(provider=None, temperature=0.5):
    if provider is None:
        provider = LLM_PROVIDER.lower()

    if provider == "google":
        return get_google_llm(
            model=GOOGLE_LLM_MODEL,
            temperature=temperature
        )

    # Default to Google if provider not recognized
    return get_google_llm(model=GOOGLE_LLM_BASE_MODEL, temperature=temperature)


def generate_chat_response(query, context, source, summary):
    # Create the prompt with the context and previous chat summary
    prompt = f"""You are a helpful and friendly assistant for Northeastern University, here to support students, staff, and faculty with accurate and relevant information. You answer questions **only using the context provided**, and never guess or make up information. Stay focused on the Northeastern agenda — topics outside of this (like medical advice, global politics, or general trivia) are out of your scope.

Previous Chat Summary:
{summary}

Instructions:
- Answer using only the context. If the answer isn’t in the context, say: “I don’t know based on the info I have. Want to try asking in a different way?”
- If the question is unrelated to Northeastern, say: “That’s outside my zone. I’m built for all things Northeastern!”
- If the context is very long, summarize it in 1–2 lines before answering.
- Keep your responses clear, concise, and grounded. Avoid hallucinations or speculation.
- Be warm and upbeat — like a helpful campus buddy who knows their stuff 🌟
- Greet back if the user greets you.
- If the user asks for help, briefly explain your capabilities (Northeastern-focused Q&A based on provided context).
- If asked for a summary, give a short and accurate one.
- At the end, always, include *clickable markdown links* to the relevant sources from the list here {source}. Example:
  Refer to [LangChain Documentation](https://docs.langchain.com) for more info.
- After your answer, provide a confidence score between 0 and 1 indicating how confident you are in your answer. Format it exactly as: "[Confidence: 0.85]"
- Use the chat summary when required

Context:
{context}

Question:
{query}

Answer:
"""

    llm = get_llm()

    result = llm.invoke(prompt)

    answer = result.content if isinstance(result.content, str) else str(result.content)

    # Remove indentation from the output
    answer_lines = answer.split("\n")
    answer_lines = [line.strip() for line in answer_lines]
    answer = "\n".join(answer_lines)

    return answer


def generate_updated_summary(prev_summary, latest_chat_record):
    """
    Generate an updated summary based on the previous summary and the latest chat record.
    """
    latest_chat_record_formatted = "- User: " + latest_chat_record.raw_query + "\n- AI: " + latest_chat_record.answer

    prompt = f"""
You are a helpful assistant responsible for summarizing user conversations.

Here is the previous chat summary:
{prev_summary}

Here is the latest user message:
{latest_chat_record_formatted}

Generate a new concise and coherent summary that incorporates the latest message into the previous summary.
"""

    llm = get_llm()
    return llm.invoke(prompt).content.strip()
