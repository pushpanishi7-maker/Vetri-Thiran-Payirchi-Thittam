from google import genai
from google.genai import types
from config import GEMINI_API_KEY, GEMINI_MODEL

class GeminiDocumentGenerator:
    """Handles online legal document generation using Google AI Studio Gemini models."""

    def __init__(self, api_key: str = None, model_name: str = None):
        self.api_key = api_key or GEMINI_API_KEY
        self.model_name = model_name or GEMINI_MODEL

    def _get_client(self):
        if not self.api_key:
            raise ValueError(
                "Gemini API Key is missing. Provide it in the UI sidebar or set GEMINI_API_KEY in your .env file."
            )
        return genai.Client(api_key=self.api_key)

    def generate_document(self, document_type: str, parties: str, terms: str, dates: str) -> str:
        client = self._get_client()

        prompt = f"""
You are an expert corporate legal counsel and contract attorney.
Draft an exhaustive, professionally structured, enforceable legal agreement based on the parameters provided below:

Document Type: {document_type}
Involved Parties: {parties}
Effective Date: {dates}
Key Terms & Agreed Conditions:
{terms}

Drafting Requirements:
1. Include a formal title, preamble, and recitals (WITNESSETH clauses).
2. Clearly declare definitions and party designations (e.g., Client, Contractor, Tenant, Landlord).
3. Draft clear, numbered operational clauses covering: Services/Scope, Compensation & Payment Terms, Term & Termination, Intellectual Property, Confidentiality, Warranties & Indemnification, Governing Law & Jurisdiction, Severability, and Entire Agreement.
4. Incorporate all user-specified terms faithfully into clear contractual obligations.
5. Conclude with formal signature execution blocks for all parties, including date and title placeholders.
6. Maintain neutral, binding, and professional legal language without explanatory conversational remarks.
"""
        response = client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.2)
        )
        if not response or not response.text:
            raise RuntimeError("Gemini failed to return text content.")
        return response.text.strip()