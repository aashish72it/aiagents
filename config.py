
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST")
LLM_MODEL = os.getenv("LLM_MODEL")
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.2"))
GROQ_ENDPOINT = os.getenv("GROQ_ENDPOINT", "https://api.groq.com/openai/v1/chat/completions")
DBT_DIR = os.getenv("DBT_DIR", "dbt_models")
# Toggle debug logging
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
