import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

HISTORY_DIR = Path(__file__).resolve().parent / "data"
HISTORY_FILE = HISTORY_DIR / "history.json"

def _ensure_storage():
    """Ensures data directory and history file exist."""
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    if not HISTORY_FILE.exists():
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, indent=2)

def get_all_history() -> List[Dict]:
    """Retrieves all past document generation history, sorted latest first."""
    _ensure_storage()
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return sorted(data, key=lambda x: x.get("timestamp", ""), reverse=True)
            return []
    except Exception as e:
        print(f"[HistoryManager] Error reading history: {e}")
        return []

def add_document_to_history(
    document_type: str,
    parties: str,
    terms: str,
    dates: str,
    model_provider: str,
    content: str
) -> Dict:
    """Saves a newly generated or updated legal document into history."""
    _ensure_storage()
    history = get_all_history()

    doc_id = f"LE-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    record = {
        "id": doc_id,
        "timestamp": timestamp_str,
        "document_type": document_type,
        "parties": parties,
        "terms": terms,
        "dates": dates,
        "model_provider": model_provider,
        "content": content,
        "word_count": len(content.split())
    }

    # Add to beginning of list
    history.insert(0, record)

    # Keep up to 50 most recent documents
    history = history[:50]

    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)
        print(f"[HistoryManager] Successfully saved document {doc_id} to history.")
    except Exception as e:
        print(f"[HistoryManager] Failed to save history: {e}")

    return record

def update_history_content(doc_id: str, new_content: str) -> bool:
    """Updates the content of an existing document in history after user edits."""
    _ensure_storage()
    history = get_all_history()
    updated = False

    for item in history:
        if item.get("id") == doc_id:
            item["content"] = new_content
            item["word_count"] = len(new_content.split())
            item["last_edited"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            updated = True
            break

    if updated:
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2)
            print(f"[HistoryManager] Updated document {doc_id} with user edits.")
            return True
        except Exception as e:
            print(f"[HistoryManager] Failed to update document {doc_id}: {e}")
    return False

def delete_history_item(doc_id: str) -> bool:
    """Removes a specific document from history."""
    _ensure_storage()
    history = get_all_history()
    new_history = [item for item in history if item.get("id") != doc_id]

    if len(new_history) != len(history):
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(new_history, f, indent=2)
            print(f"[HistoryManager] Deleted document {doc_id}.")
            return True
        except Exception as e:
            print(f"[HistoryManager] Failed to delete history item: {e}")
    return False

def clear_all_history() -> bool:
    """Clears all history records."""
    _ensure_storage()
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, indent=2)
        print("[HistoryManager] Cleared all document history.")
        return True
    except Exception as e:
        print(f"[HistoryManager] Failed to clear history: {e}")
        return False
