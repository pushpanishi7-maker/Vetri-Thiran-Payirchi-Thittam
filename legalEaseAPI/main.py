import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from legalEaseAPI.routes import router
from config import BACKEND_HOST, BACKEND_PORT

app = FastAPI(
    title="LegalEase AI Legal Document Generator API",
    description="Backend API powering legal document generation using Gemini and local LLaMA 3.",
    version="1.0.0"
)

# Enable CORS for Streamlit frontend interaction
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Attach API routes
app.include_router(router)

@app.get("/")
def home():
    return {
        "status": "online",
        "message": "Welcome to LegalEase AI Legal Document Generator API",
        "supported_models": ["gemini-1.5-pro", "llama3 (local)"]
    }

if __name__ == "__main__":
    uvicorn.run("legalEaseAPI.main:app", host=BACKEND_HOST, port=BACKEND_PORT, reload=True)