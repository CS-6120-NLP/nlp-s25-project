import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///nu_chatbot.db")
PERMISSION_THRESHOLD = float(os.getenv("PERMISSION_THRESHOLD", 0.8))
CHAT_HISTORY_WINDOW = 40
