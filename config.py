import os

from dotenv import load_dotenv

load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "google")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/db/sql/sql.db")
API_PREFIX = os.getenv("API_PREFIX", "/api/v1")
PERMISSION_THRESHOLD = float(os.getenv("PERMISSION_THRESHOLD", 0.8))

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GOOGLE_LLM_BASE_MODEL = os.getenv("GOOGLE_LLM_BASE_MODEL", "")
GOOGLE_LLM_MODEL = os.getenv("GOOGLE_LLM_MODEL", "")

COHERE_API_KEY = os.getenv("COHERE_API_KEY", "")
