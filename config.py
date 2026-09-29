import os
from pathlib import Path
from dotenv import load_dotenv

# Base Directory paths
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"

# Load environment variables
load_dotenv(dotenv_path=ENV_PATH)

# AI Model Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")

# Local Offline LLaMA 3 Configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

# Server Configuration
BACKEND_HOST = os.getenv("BACKEND_HOST", "127.0.0.1")
BACKEND_PORT = int(os.getenv("BACKEND_PORT", 8000))
BACKEND_URL = f"http://{BACKEND_HOST}:{BACKEND_PORT}"

# Image Asset Paths
IMAGE_DIR = BASE_DIR / "Image"
LOGO_PATH = IMAGE_DIR / "Logo.png"
INVERSE_LOGO_PATH = IMAGE_DIR / "inverseLogo.png"