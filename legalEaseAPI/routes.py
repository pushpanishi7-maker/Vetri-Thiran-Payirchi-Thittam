import time
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ai_core.generator import DocumentGeneratorManager
from history_manager import (
    get_all_history,
    add_document_to_history,
    delete_history_item,
    clear_all_history,
    update_history_content
)

router = APIRouter()

class DocumentRequest(BaseModel):
    document_type: str = Field(..., example="Freelance Work Contract")
    parties: str = Field(..., example="Jane Doe (Service Provider), TechNova Inc. (Client)")
    terms: str = Field(..., example="Deliverables by May 15; Payment within 7 days; Client retains IP")
    dates: str = Field(..., example="April 15, 2025")
    model_provider: str = Field(default="gemini", example="gemini") # "gemini" or "llama3"
    api_key: Optional[str] = Field(default=None, example="AIzaSy...")

class UpdateHistoryRequest(BaseModel):
    doc_id: str
    content: str

@router.post("/generate")
def generate_legal_document(request: DocumentRequest):
    """Processes document creation requests via the chosen AI backend with detailed terminal workflow logging."""
    t_start = time.time()
    print("\n" + "=" * 65)
    print("[API Route: /generate] Incoming Request Received")
    print(f"   * Type      : {request.document_type}")
    print(f"   * Provider  : {request.model_provider}")
    print(f"   * Parties   : {request.parties}")
    print(f"   * Effective : {request.dates}")
    print("=" * 65)

    try:
        manager = DocumentGeneratorManager(
            provider=request.model_provider,
            api_key=request.api_key
        )
        content = manager.generate(
            document_type=request.document_type,
            parties=request.parties,
            terms=request.terms,
            dates=request.dates
        )

        # Automatically archive to history
        record = add_document_to_history(
            document_type=request.document_type,
            parties=request.parties,
            terms=request.terms,
            dates=request.dates,
            model_provider=request.model_provider,
            content=content
        )

        print(f"[API Route: /generate] [SAVED] Document archived to history (ID: {record['id']})")
        print(f"[API Route: /generate] [TIME] Total cycle time: {time.time() - t_start:.2f}s\n")

        return {
            "status": "success",
            "document": content,
            "doc_id": record["id"],
            "timestamp": record["timestamp"]
        }
    except ValueError as ve:
        print(f"[API Route: /generate] [ERROR] Validation: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except ConnectionError as ce:
        print(f"[API Route: /generate] [ERROR] Connection: {ce}")
        raise HTTPException(status_code=503, detail=str(ce))
    except Exception as e:
        print(f"[API Route: /generate] [ERROR] Internal: {e}")
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

@router.get("/history")
def fetch_history():
    """Returns all past generated document records."""
    history = get_all_history()
    return {"status": "success", "count": len(history), "history": history}

@router.post("/history/update")
def update_document(request: UpdateHistoryRequest):
    """Updates stored document with user-edited text."""
    success = update_history_content(request.doc_id, request.content)
    if not success:
        raise HTTPException(status_code=404, detail="Document ID not found in history.")
    return {"status": "success", "message": "Document updated."}

@router.delete("/history/{doc_id}")
def delete_document(doc_id: str):
    """Removes a document from history by ID."""
    success = delete_history_item(doc_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document ID not found.")
    return {"status": "success", "message": f"Deleted {doc_id}"}

@router.delete("/history")
def clear_history():
    """Wipes entire document history."""
    clear_all_history()
    return {"status": "success", "message": "All history cleared."}