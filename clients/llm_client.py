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
