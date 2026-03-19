import os
from dotenv import load_dotenv

load_dotenv()

# --- API Configuration ---
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

# --- Model Configuration ---
MODEL_NAME = "llama-3.3-70b-versatile"
SQL_MAX_TOKENS = 500
EXPLAIN_MAX_TOKENS = 300

# --- App Configuration ---
APP_TITLE = "Text-to-SQL Agent"
APP_SUBTITLE = "Connect any database and ask questions in plain English"
MAX_HISTORY_DISPLAY = 10

# --- Supported DB types ---
SUPPORTED_DBS = ["SQLite", "PostgreSQL", "MySQL"]