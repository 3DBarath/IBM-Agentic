"""Configuration and environment settings."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file
load_dotenv(BASE_DIR / ".env")

OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY", "")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "https://ollama.com").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gpt-oss:120b")
PORT = int(os.getenv("PORT", 8000))
HOST = os.getenv("HOST", "0.0.0.0")

# Uploads directory
UPLOADS_DIR = BASE_DIR / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
