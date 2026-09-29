import requests
from config import OLLAMA_BASE_URL, OLLAMA_MODEL

class LlamaDocumentGenerator:
    """Handles offline legal document generation via a local Ollama LLaMA 3 instance."""

    def __init__(self, base_url: str = None, model_name: str = None):
        self.base_url = (base_url or OLLAMA_BASE_URL).rstrip("/")
        self.model_name = model_name or OLLAMA_MODEL

    def generate_document(self, document_type: str, parties: str, terms: str, dates: str) -> str:
        prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
You are an expert contract attorney. Draft formal, legally binding, highly structured legal documents with full clauses, terms, and signature blocks. Do not add introductory chit-chat. Return only the final legal document text.<|eot_id|>
<|start_header_id|>user<|end_header_id|>
Draft a comprehensive legal document based on these parameters:
Document Type: {document_type}
Parties Involved: {parties}
Effective Date: {dates}
Terms & Conditions:
{terms}

Requirements:
- Formal legal title, recitals, and defined terms.
- Numbered sections for scope, payment, confidentiality, termination, liability, governing law, and severability.
- Formal closing with signature execution lines.
<|eot_id|>
<|start_header_id|>assistant<|end_header_id|>
"""
        endpoint = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.2,
                "top_p": 0.9,
                "num_ctx": 2048,
                "num_predict": 1200
            }
        }

        try:
            response = requests.post(endpoint, json=payload, timeout=600)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "").strip()
        except requests.exceptions.ConnectionError:
            raise ConnectionError(
                f"Cannot connect to local Ollama at '{self.base_url}'. "
                "Ensure Ollama is running locally (e.g., execute 'ollama run llama3' in your terminal)."
            )
        except Exception as e:
            raise RuntimeError(f"Local LLaMA generation error: {str(e)}")