"""Application configuration loaded from environment variables."""

import os

from dotenv import load_dotenv


load_dotenv()

OLLAMA_URL = os.getenv(
    "OLLAMA_URL", "http://localhost:11434/api/generate"
)
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
OLLAMA_TIMEOUT_SECONDS = 120

