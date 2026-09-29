import streamlit as st
import requests
import time
from pathlib import Path
from PIL import Image

import sys
# Ensure the root folder is discoverable by Python imports
sys.path.append(str(Path(__file__).resolve().parent.parent))

from config import BACKEND_URL, LOGO_PATH, INVERSE_LOGO_PATH, GEMINI_API_KEY
from ai_core.generator import sanitize_text, format_pdf, format_html_preview
from history_manager import (
    get_all_history,
    add_document_to_history,
    delete_history_item,
    clear_all_history,
    update_history_content
)

# Configure Streamlit page
st.set_page_config(
    page_title="LegalEase - AI Legal Document Generator",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State
if "generated_text" not in st.session_state:
    st.session_state.generated_text = ""
if "doc_type" not in st.session_state:
    st.session_state.doc_type = "Non-Disclosure Agreement (NDA)"
if "parties" not in st.session_state:
    st.session_state.parties = "Alice Smith (Disclosing Party), Bob Jones (Receiving Party)"
if "terms" not in st.session_state:
    st.session_state.terms = "Receiving Party must keep all technical and financial data confidential; Duration of confidentiality is 3 years; Materials returned upon termination."
if "dates" not in st.session_state:
    st.session_state.dates = "October 5, 2026"
if "current_doc_id" not in st.session_state:
    st.session_state.current_doc_id = None
if "edit_buffer" not in st.session_state:
    st.session_state.edit_buffer = ""

# -------------------------------------------------------------
# Sidebar: Settings, History Quick-Access & Health Status
# -------------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚙️ Engine Settings")
    
    # Model Provider Selection
    model_choice = st.radio(
        "Select AI Model Provider:",
        options=["Google Gemini (Online Cloud)", "Meta LLaMA 3 (Offline / Local)"],
        index=0
    )
    
    selected_provider = "gemini" if "Gemini" in model_choice else "llama3"

    user_api_key = ""
    if selected_provider == "gemini":
        st.markdown("#### Google AI Studio Key")
        user_api_key = st.text_input(
            "Gemini API Key:",
            type="password",
            value=GEMINI_API_KEY,
            help="Loaded from .env if set. You can override it here directly."
        )
        if not user_api_key:
            st.warning("⚠️ Enter a Gemini API Key or set GEMINI_API_KEY in .env.")
        else:
            st.success("✅ Gemini Key ready.")
    else:
        st.markdown("#### Offline Mode: LLaMA 3")
        st.info("Uses local Ollama at `http://localhost:11434`. Runs 100% locally on your machine.")
        st.caption("💡 Runs on CPU. Generation takes ~2-4 minutes for full legal agreements.")

    st.markdown("---")
    
    # Backend Health Check
    try:
        health_resp = requests.get(f"{BACKEND_URL}/", timeout=2)
        if health_resp.status_code == 200:
            st.sidebar.caption("🟢 Backend API: **Connected (Port 8000)**")
        else:
            st.sidebar.caption("🟡 Backend API: **Unexpected Status**")
    except Exception:
        st.sidebar.caption("🔴 Backend API: **Disconnected** (Run run.bat)")

    st.markdown("---")
    # Quick History Drawer in Sidebar
    st.markdown("### 📜 Recent History")
    history_items = get_all_history()
    
    if not history_items:
        st.caption("No agreements generated yet.")
    else:
        st.caption(f"Stored agreements: **{len(history_items)}**")
        for item in history_items[:5]:
            with st.expander(f"📄 {item.get('document_type', 'Agreement')[:24]}..."):
                st.caption(f"**Date:** {item.get('timestamp', 'N/A')}")
                st.caption(f"**Parties:** {item.get('parties', 'N/A')[:40]}...")
                st.caption(f"**Engine:** {item.get('model_provider', 'N/A').upper()} ({item.get('word_count', 0)} words)")
                
                col_load, col_del = st.columns([2, 1])
                with col_load:
                    if st.button("📂 Load", key=f"side_load_{item['id']}", use_container_width=True):
                        print(f"\n[LegalEase UI] [LOAD] Loading document '{item['id']}' from history into editor...")
                        st.session_state.generated_text = item.get("content", "")
                        st.session_state.edit_buffer = item.get("content", "")
                        st.session_state.doc_type = item.get("document_type", "")
                        st.session_state.parties = item.get("parties", "")
                        st.session_state.terms = item.get("terms", "")
                        st.session_state.dates = item.get("dates", "")
                        st.session_state.current_doc_id = item.get("id")
                        st.rerun()
                with col_del:
                    if st.button("🗑️", key=f"side_del_{item['id']}", use_container_width=True):
                        delete_history_item(item["id"])
                        print(f"[LegalEase UI] [DELETE] Deleted document '{item['id']}' from history.")
                        st.rerun()

        if st.button("🧹 Clear All History", use_container_width=True):
            clear_all_history()
            print("[LegalEase UI] [CLEAR] Document history wiped by user.")
            st.rerun()


# -------------------------------------------------------------
# Main Application Header & Branding
# -------------------------------------------------------------
col_logo, col_title = st.columns([1, 4])
with col_logo:
    if Path(LOGO_PATH).exists():
        st.image(str(LOGO_PATH), width=110)
    else:
        st.markdown("<h1 style='text-align: center;'>⚖️</h1>", unsafe_allow_html=True)
with col_title:
    st.markdown("<h2 style='margin-bottom: 2px; color: #F8FAFC;'>LegalEase AI Legal Suite</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94A3B8; margin-top: -6px; font-size: 14px;'>Professional Legal Document Generator, Live In-App Reviewer & Executive PDF Exporter</p>", unsafe_allow_html=True)

st.markdown("---")

# Main Application Tabs
tab_create, tab_review, tab_history = st.tabs([
    "📝 1. Create Legal Agreement",
    "📑 2. Live Review & In-App Editor",
    "📜 3. Document Archive & History"
])

# -------------------------------------------------------------
# TAB 1: Document Creation Form
# -------------------------------------------------------------
with tab_create:
    st.markdown("#### Contract Drafting Parameters")
    
    with st.form("contract_form"):
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            doc_type_input = st.text_input(
                "Document Type (e.g., NDA, Employment Agreement, SaaS Contract):",
                value=st.session_state.doc_type,
                placeholder="Non-Disclosure Agreement (NDA)"
            )
            dates_input = st.text_input(
                "Effective Date:",
                value=st.session_state.dates,
                placeholder="October 5, 2026"
            )
        with col_f2:
            parties_input = st.text_input(
                "Parties Involved (Full Legal Names & Roles):",
                value=st.session_state.parties,
                placeholder="Alice Smith (Disclosing Party), Bob Jones (Receiving Party)"
            )
            
        terms_input = st.text_area(
            "Agreed Terms & Conditions (Separate distinct clauses with semicolons ';'):",
            value=st.session_state.terms,
            placeholder="Receiving Party agrees to strict confidentiality; Duration is 3 years; All technical materials must be returned upon request; Governing law is California.",
            height=120
        )

        generate_button = st.form_submit_button("⚡ Generate Legal Document", use_container_width=True)

    if generate_button:
        if not doc_type_input or not parties_input or not terms_input or not dates_input:
            st.error("⚠️ Please fill in all fields before generating.")
        elif selected_provider == "gemini" and not user_api_key:
            st.error("⚠️ Gemini API Key is required. Please provide it in the sidebar.")
        else:
            # Update state with latest input values
            st.session_state.doc_type = doc_type_input
            st.session_state.parties = parties_input
            st.session_state.terms = terms_input
            st.session_state.dates = dates_input

            print("\n" + "=" * 65)
            print("[LegalEase UI Workflow] Dispatching generation request:")
            print(f"   * Document Type : {doc_type_input}")
            print(f"   * Model Provider: {model_choice}")
            print(f"   * Effective Date: {dates_input}")
            print("=" * 65)

            payload = {
                "document_type": doc_type_input,
                "parties": parties_input,
                "terms": terms_input,
                "dates": dates_input,
                "model_provider": selected_provider,
                "api_key": user_api_key if selected_provider == "gemini" else None
            }

            status_msg = f"Drafting legal document using {model_choice}... "
            if selected_provider == "llama3":
                status_msg += " (Local CPU mode: Please allow 2-4 minutes for comprehensive clause generation)"

            with st.spinner(status_msg):
                start_req = time.time()
                try:
                    resp = requests.post(f"{BACKEND_URL}/generate", json=payload, timeout=600)
                    if resp.status_code == 200:
                        data = resp.json()
                        raw_content = data.get("document", "")
                        doc_id = data.get("doc_id")

                        st.session_state.generated_text = raw_content
                        st.session_state.edit_buffer = raw_content
                        st.session_state.current_doc_id = doc_id

                        elapsed = time.time() - start_req
                        print(f"[LegalEase UI Workflow] [OK] Generation complete in {elapsed:.2f}s. Stored ID: {doc_id}")
                        st.success(f"🎉 Document Generated Successfully in {elapsed:.1f}s! Switch to Tab 2 to Review & Edit.")
                    else:
                        detail = resp.json().get("detail", "Error encountered.")
                        print(f"[LegalEase UI Workflow] [ERROR] Backend responded: {detail}")
                        st.error(f"Generation Failed: {detail}")
                except requests.exceptions.ConnectionError:
                    print("[LegalEase UI Workflow] [ERROR] Connection refused to FastAPI backend.")
                    st.error("Cannot reach the FastAPI backend at http://127.0.0.1:8000. Ensure run.bat is running.")
                except Exception as e:
                    print(f"[LegalEase UI Workflow] [ERROR] Unexpected exception: {e}")
                    st.error(f"Generation error: {str(e)}")

# -------------------------------------------------------------
# TAB 2: Live Review, In-App Editor & PDF Export ONLY
# -------------------------------------------------------------
with tab_review:
    current_text = st.session_state.generated_text

    if not current_text:
        st.info("👈 No document active yet. Generate a contract in Tab 1 or load an existing one from Tab 3 / History.")
    else:
        st.markdown(f"### ⚖️ Reviewing: **{st.session_state.doc_type}**")
        st.caption(f"Parties: {st.session_state.parties} | Effective: {st.session_state.dates}")

        # Split screen: Editor on the Left, Live Formatted Preview on the Right
        col_edit, col_prev = st.columns([1, 1], gap="medium")

        with col_edit:
            st.markdown("#### ✏️ In-App Document Editor")
            st.caption("Directly modify clauses, fix names, or add custom terms below:")

            edited_text = st.text_area(
                label="Contract Editor Area",
                value=st.session_state.generated_text,
                height=520,
                key="in_app_text_editor",
                label_visibility="collapsed"
            )

            col_btn_apply, col_btn_reset = st.columns([2, 1])
            with col_btn_apply:
                if st.button("💾 Apply & Save Edits", use_container_width=True):
                    st.session_state.generated_text = edited_text
                    if st.session_state.current_doc_id:
                        update_history_content(st.session_state.current_doc_id, edited_text)
                    print(f"[LegalEase UI] [EDIT] User saved edits for document. New word count: {len(edited_text.split())}")
                    st.success("✅ Changes applied to live preview and PDF export!")
                    st.rerun()

            with col_btn_reset:
                if st.button("🔄 Discard", use_container_width=True):
                    st.rerun()

        with col_prev:
            st.markdown("#### 📄 Live Formatted Preview")
            st.caption("Visual representation styled with executive legal hierarchy:")
            
            # Formatted HTML Preview Box
            active_content = edited_text if edited_text else st.session_state.generated_text
            preview_html = format_html_preview(active_content)
            st.markdown(
                f"""
                <div style="background-color: #0F172A; padding: 25px; border-radius: 8px; border: 1px solid #334155; height: 520px; overflow-y: auto; box-shadow: inset 0 2px 4px rgba(0,0,0,0.5);">
                    {preview_html}
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("---")

        # Exclusive PDF Export Section (No DOCX, No TXT)
        st.markdown("### 📥 Formal PDF Export")
        st.write("Generate a publication-grade legal PDF featuring company branding, formal headers, styled clause sections, and dual-party signature blocks:")

        filename_clean = (st.session_state.doc_type or "legal_agreement").strip().lower().replace(" ", "_")

        # Compile PDF from current active text (including any manual edits made)
        content_to_export = edited_text if edited_text else st.session_state.generated_text
        
        pdf_bytes = format_pdf(
            text=content_to_export,
            doc_type=st.session_state.doc_type,
            parties=st.session_state.parties,
            dates=st.session_state.dates,
            logo_path=str(LOGO_PATH) if Path(LOGO_PATH).exists() else None
        )

        st.download_button(
            label="📕 Download Formatted Legal PDF",
            data=pdf_bytes,
            file_name=f"{filename_clean}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

# -------------------------------------------------------------
# TAB 3: Document Archive & History Management
# -------------------------------------------------------------
with tab_history:
    st.markdown("### 📜 Document Generation Archive")
    st.write("All previously drafted contracts are preserved locally for audit, review, and re-export.")

    all_docs = get_all_history()

    if not all_docs:
        st.info("No documents archived in history yet. Any document created in Tab 1 will be automatically logged here.")
    else:
        st.markdown(f"**Total Records:** `{len(all_docs)}` documents stored")

        for idx, doc in enumerate(all_docs):
            doc_id = doc.get("id", f"doc_{idx}")
            with st.expander(f"📑 {doc.get('document_type', 'Agreement')} — {doc.get('timestamp', 'N/A')}", expanded=(idx == 0)):
                h_col1, h_col2, h_col3 = st.columns([2, 2, 1])
                with h_col1:
                    st.write(f"**Parties:** {doc.get('parties', 'N/A')}")
                    st.write(f"**Effective Date:** {doc.get('dates', 'N/A')}")
                with h_col2:
                    st.write(f"**Engine:** `{doc.get('model_provider', 'N/A').upper()}`")
                    st.write(f"**Word Count:** `{doc.get('word_count', 0)} words`")
                with h_col3:
                    if st.button("📂 Open & Edit", key=f"main_load_{doc_id}", use_container_width=True):
                        st.session_state.generated_text = doc.get("content", "")
                        st.session_state.edit_buffer = doc.get("content", "")
                        st.session_state.doc_type = doc.get("document_type", "")
                        st.session_state.parties = doc.get("parties", "")
                        st.session_state.terms = doc.get("terms", "")
                        st.session_state.dates = doc.get("dates", "")
                        st.session_state.current_doc_id = doc_id
                        print(f"[LegalEase UI] [LOAD] Switched active contract to archived document: '{doc_id}'")
                        st.success(f"Loaded '{doc.get('document_type')}' into Tab 2.")
                        st.rerun()

                    if st.button("🗑️ Delete", key=f"main_del_{doc_id}", use_container_width=True):
                        delete_history_item(doc_id)
                        print(f"[LegalEase UI] [DELETE] Deleted archived record: '{doc_id}'")
                        st.rerun()

                # Preview snippet
                st.markdown("**Preview Excerpt:**")
                snippet = doc.get("content", "")[:350] + ("..." if len(doc.get("content", "")) > 350 else "")
                st.code(snippet, language="markdown")

        st.markdown("<br/>", unsafe_allow_html=True)
        if st.button("🚨 Clear Complete Archive", use_container_width=True):
            clear_all_history()
            print("[LegalEase UI] [PURGE] Entire document history purged by user.")
            st.rerun()