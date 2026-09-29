import re
import io
import time
from pathlib import Path
from fpdf import FPDF
from fpdf.enums import XPos, YPos

from ai_core.gemini_generator import GeminiDocumentGenerator
from ai_core.llama_generator import LlamaDocumentGenerator

def sanitize_text(text: str) -> str:
    """Sanitizes text by replacing typographic symbols to ensure clean PDF rendering."""
    if not text:
        return ""
    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2014": " - ",
        "\u2013": " - ",
        "\u2026": "...",
        "\u00a0": " ",
        "\u2022": "*",
        "\u25cf": "*",
        "\u00a7": "Section ",
        "\u2122": "(TM)",
        "\u00ae": "(R)",
        "\u00a9": "(C)",
        "\u20ac": "EUR ",
        "\u00a3": "GBP ",
        "\u20b9": "INR ",
    }
    for orig, repl in replacements.items():
        text = text.replace(orig, repl)
    
    # Strip non-latin1 characters for basic FPDF compatibility
    return text.encode("latin-1", "replace").decode("latin-1")


class DocumentGeneratorManager:
    """Unified generator router handling online Gemini and offline LLaMA 3 with terminal workflow logging."""

    def __init__(self, provider: str = "gemini", api_key: str = None):
        self.provider = provider.lower()
        self.api_key = api_key

    def generate(self, document_type: str, parties: str, terms: str, dates: str) -> str:
        start_time = time.time()
        provider_label = "Google Gemini (Online Cloud)" if self.provider == "gemini" else "Meta LLaMA 3 (Offline / Local)"
        
        print("\n" + "=" * 70)
        print("[LegalEase Workflow] DOCUMENT GENERATION INITIATED")
        print(f"|-- [Step 1/5] Request Parameters:")
        print(f"|   |-- Document Type : {document_type}")
        print(f"|   |-- Parties       : {parties}")
        print(f"|   |-- Effective Date: {dates}")
        print(f"|   |-- Key Terms     : {terms[:80]}..." if len(terms) > 80 else f"|   |-- Key Terms     : {terms}")
        print(f"|-- [Step 2/5] Selected Engine Provider: {provider_label}")

        if self.provider == "llama3":
            print("|-- [Step 3/5] Initializing local LLaMA 3 engine (Ollama)...")
            generator = LlamaDocumentGenerator()
            print("|-- [Step 4/5] Running local CPU inference (Generating full clauses)...")
            content = generator.generate_document(document_type, parties, terms, dates)
        else:
            print("|-- [Step 3/5] Initializing Google Gemini API Client...")
            generator = GeminiDocumentGenerator(api_key=self.api_key)
            print("|-- [Step 4/5] Sending prompt to Gemini Cloud and awaiting response...")
            content = generator.generate_document(document_type, parties, terms, dates)

        elapsed = time.time() - start_time
        word_count = len(content.split())
        print(f"|-- [Step 5/5] Document Successfully Generated:")
        print(f"|   |-- Word Count    : {word_count} words")
        print(f"|   |-- Characters    : {len(content)} chars")
        print(f"|   |-- Duration      : {elapsed:.2f} seconds")
        print(f"+-- [LegalEase Workflow] COMPLETED SUCCESSFULLY [OK]")
        print("=" * 70 + "\n")
        
        return content


# -------------------------------------------------------------
# Professional Executive Legal PDF Layout
# -------------------------------------------------------------

class LegalPDF(FPDF):
    """Publication-grade legal document PDF formatter with running headers, footers, and executive layout."""

    def __init__(self, doc_type: str = "LEGAL AGREEMENT", logo_path: str = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.doc_type = doc_type.upper()
        self.logo_path = logo_path
        self.set_auto_page_break(auto=True, margin=22)

    def header(self):
        # Running header only on pages 2 and onward
        if self.page_no() > 1:
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(100, 116, 139)  # Slate grey
            self.cell(100, 6, f"{self.doc_type[:45]} | CONFIDENTIAL", align="L")
            self.cell(80, 6, "LEGALEASE AI LEGAL SUITE", align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            # Thin top rule
            self.set_draw_color(203, 213, 225)
            self.set_line_width(0.3)
            self.line(15, 14, 195, 14)
            self.ln(6)

    def footer(self):
        self.set_y(-16)
        # Thin footer rule
        self.set_draw_color(203, 213, 225)
        self.set_line_width(0.3)
        self.line(15, self.get_y(), 195, self.get_y())
        self.ln(2)
        
        self.set_font("Helvetica", "", 8)
        self.set_text_color(148, 163, 184)
        self.cell(90, 8, "CONFIDENTIAL & LEGALLY BINDING DOCUMENT", align="L")
        self.cell(90, 8, f"Page {self.page_no()} of {{nb}}", align="R")


def format_pdf(text: str, doc_type: str, parties: str = "", dates: str = "", logo_path: str = None) -> bytes:
    """Formats AI-generated legal text into an executive-grade, beautifully formatted legal PDF."""
    clean_text = sanitize_text(text)
    clean_title = sanitize_text(doc_type or "Legal Agreement").upper()

    print(f"\n[LegalEase PDF] [Export] Compiling executive PDF for: '{clean_title}'...")

    pdf = LegalPDF(doc_type=clean_title, logo_path=logo_path)
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_margins(15, 18, 15)

    # 1. Top Accent Brand Line (Navy Blue)
    pdf.set_fill_color(26, 54, 93)  # #1A365D
    pdf.rect(15, 18, 180, 2.5, "F")
    pdf.ln(5)

    # 2. Header / Logo Section
    if logo_path and Path(logo_path).exists():
        try:
            pdf.image(str(logo_path), x=88, y=23, w=34)
            pdf.ln(24)
        except Exception:
            pdf.ln(8)
    else:
        pdf.ln(4)

    # 3. Document Formal Title
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(26, 54, 93)  # Deep Navy
    pdf.multi_cell(180, 8, clean_title, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    # Subtitle
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(180, 6, "Exclusively Drafted & Verified via LegalEase Intelligence", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(3)

    # Decorative Divider
    pdf.set_draw_color(26, 54, 93)
    pdf.set_line_width(0.6)
    pdf.line(60, pdf.get_y(), 150, pdf.get_y())
    pdf.ln(6)

    # 4. Document Metadata Card (If parties or dates provided)
    if parties or dates:
        card_start_y = pdf.get_y()
        pdf.set_fill_color(248, 250, 252)  # #F8FAFC
        pdf.set_draw_color(226, 232, 240)  # #E2E8F0
        pdf.set_line_width(0.3)
        pdf.rect(15, card_start_y, 180, 18, "DF")
        
        pdf.set_xy(18, card_start_y + 2)
        pdf.set_font("Helvetica", "B", 8.5)
        pdf.set_text_color(51, 65, 85)
        pdf.cell(35, 6, "EFFECTIVE DATE:", align="L")
        pdf.set_font("Helvetica", "", 8.5)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(50, 6, sanitize_text(dates or "As declared herein"), align="L")

        pdf.set_font("Helvetica", "B", 8.5)
        pdf.set_text_color(51, 65, 85)
        pdf.cell(30, 6, "STATUS:", align="L")
        pdf.set_font("Helvetica", "B", 8.5)
        pdf.set_text_color(22, 101, 52)  # Green
        pdf.cell(60, 6, "LEGALLY BINDING DRAFT", align="L", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        pdf.set_xy(18, card_start_y + 9)
        pdf.set_font("Helvetica", "B", 8.5)
        pdf.set_text_color(51, 65, 85)
        pdf.cell(35, 6, "PARTIES INVOLVED:", align="L")
        pdf.set_font("Helvetica", "", 8.5)
        pdf.set_text_color(15, 23, 42)
        clean_parties = sanitize_text(parties or "Parties designated within agreement")
        pdf.cell(140, 6, clean_parties[:85] + ("..." if len(clean_parties) > 85 else ""), align="L")
        pdf.set_y(card_start_y + 22)
    else:
        pdf.ln(4)

    # 5. Document Body Rendering with Smart Markdown Parsing
    lines = clean_text.split("\n")
    in_signature_section = False

    for line in lines:
        stripped = line.strip()
        if not stripped:
            pdf.ln(2.5)
            continue

        # Detect Signature Execution Section
        if re.search(r"IN WITNESS WHEREOF|SIGNATURES|EXECUTION BLOCK", stripped, re.IGNORECASE):
            in_signature_section = True
            pdf.ln(6)
            # Section header for signatures
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_text_color(26, 54, 93)
            pdf.cell(180, 8, stripped.upper(), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_draw_color(203, 213, 225)
            pdf.line(15, pdf.get_y(), 195, pdf.get_y())
            pdf.ln(5)
            continue

        # Major Headings (## Section / SECTION / ARTICLE)
        if stripped.startswith("## ") or re.match(r"^(SECTION|ARTICLE|CLAUSE)\s+\d+", stripped, re.IGNORECASE):
            heading_clean = stripped.lstrip("#").strip()
            pdf.ln(4)
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_text_color(26, 54, 93)  # Navy
            
            # Left accent pill
            cur_y = pdf.get_y()
            pdf.set_fill_color(26, 54, 93)
            pdf.rect(15, cur_y + 1, 2.5, 5, "F")
            
            pdf.set_x(20)
            pdf.multi_cell(175, 6, heading_clean, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font("Helvetica", "", 9.5)
            pdf.set_text_color(30, 41, 59)
            pdf.ln(1.5)

        # Level 1 Heading (# Title inside markdown)
        elif stripped.startswith("# "):
            h_text = stripped.lstrip("#").strip()
            if h_text.upper() != clean_title:
                pdf.ln(3)
                pdf.set_font("Helvetica", "B", 12)
                pdf.set_text_color(26, 54, 93)
                pdf.multi_cell(180, 7, h_text, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.ln(2)

        # Subheadings (### Sub-clause)
        elif stripped.startswith("### "):
            sub_clean = stripped.lstrip("#").strip()
            pdf.ln(2.5)
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(51, 65, 85)
            pdf.multi_cell(180, 5.5, sub_clean, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font("Helvetica", "", 9.5)
            pdf.set_text_color(30, 41, 59)
            pdf.ln(1)

        # Numbered Clauses (e.g., "1. Scope of Work" or "1.1 ")
        elif re.match(r"^(\d+\.|\d+\.\d+|\([a-z]\))\s+", stripped):
            pdf.set_font("Helvetica", "", 9.5)
            pdf.set_text_color(30, 41, 59)
            pdf.set_x(18)
            try:
                pdf.multi_cell(177, 5, stripped, markdown=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            except Exception:
                pdf.multi_cell(177, 5, stripped, markdown=False, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(1.5)

        # Bullet List Items
        elif stripped.startswith("- ") or stripped.startswith("* "):
            bullet_body = stripped[2:].strip()
            pdf.set_font("Helvetica", "", 9.5)
            pdf.set_text_color(30, 41, 59)
            pdf.set_x(20)
            bullet_prefix = chr(149) + " " if chr(149) in "•" else "- "
            try:
                pdf.multi_cell(175, 5, f"- {bullet_body}", markdown=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            except Exception:
                pdf.multi_cell(175, 5, f"- {bullet_body}", markdown=False, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(1)

        # Signature Line Placeholders
        elif in_signature_section or "signature:" in stripped.lower() or "by:" in stripped.lower() or "date:" in stripped.lower():
            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(51, 65, 85)
            pdf.cell(180, 5.5, stripped, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        # Standard Body Paragraphs
        else:
            pdf.set_font("Helvetica", "", 9.5)
            pdf.set_text_color(30, 41, 59)
            pdf.set_x(15)
            try:
                pdf.multi_cell(180, 5, stripped, markdown=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            except Exception:
                pdf.multi_cell(180, 5, stripped, markdown=False, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(2)

    # 6. Fallback Dual Signature Block if not explicitly generated by model
    if not in_signature_section:
        # Check remaining space on current page
        if pdf.get_y() > 210:
            pdf.add_page()
        else:
            pdf.ln(6)

        pdf.set_font("Helvetica", "B", 10.5)
        pdf.set_text_color(26, 54, 93)
        pdf.cell(180, 7, "EXECUTION AND ACKNOWLEDGMENT", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font("Helvetica", "I", 8.5)
        pdf.set_text_color(100, 116, 139)
        pdf.cell(180, 5, "IN WITNESS WHEREOF, the duly authorized representatives have executed this Agreement.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(6)

        sig_y = pdf.get_y()
        # Party 1 Box (Left)
        pdf.set_xy(15, sig_y)
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(85, 5, "FOR AND ON BEHALF OF FIRST PARTY:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(8)
        pdf.set_x(15)
        pdf.cell(85, 5, "Signature: ___________________________", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_x(15)
        pdf.cell(85, 5, "Name:      ___________________________", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_x(15)
        pdf.cell(85, 5, "Title:       ___________________________", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_x(15)
        pdf.cell(85, 5, "Date:        ___________________________", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        # Party 2 Box (Right)
        pdf.set_xy(110, sig_y)
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(85, 5, "FOR AND ON BEHALF OF SECOND PARTY:")
        pdf.set_xy(110, sig_y + 13)
        pdf.cell(85, 5, "Signature: ___________________________")
        pdf.set_xy(110, sig_y + 18)
        pdf.cell(85, 5, "Name:      ___________________________")
        pdf.set_xy(110, sig_y + 23)
        pdf.cell(85, 5, "Title:       ___________________________")
        pdf.set_xy(110, sig_y + 28)
        pdf.cell(85, 5, "Date:        ___________________________")

    pdf_bytes = bytes(pdf.output())
    print(f"[LegalEase PDF] [OK] Successfully compiled executive PDF ({len(pdf_bytes)} bytes)\n")
    return pdf_bytes


def format_docx(text: str, doc_type: str, terms_raw: str = "", logo_path: str = None) -> bytes:
    """Legacy DOCX generator kept for compatibility."""
    from docx import Document
    doc = Document()
    doc.add_heading(doc_type, 0)
    for line in text.split("\n"):
        if line.strip():
            doc.add_paragraph(line.strip())
    file_stream = io.BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    return file_stream.getvalue()


def format_html_preview(text: str) -> str:
    """Transforms raw document markdown into styled executive legal preview HTML."""
    if not text:
        return ""
    lines = text.split("\n")
    html_out = []
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            html_out.append("<div style='height: 10px;'></div>")
        elif stripped.startswith("## "):
            clause_title = stripped[3:].strip()
            html_out.append(f"""
            <div style='margin-top: 18px; margin-bottom: 8px; border-left: 3px solid #3B82F6; padding-left: 10px;'>
                <strong style='color: #60A5FA; font-size: 15px; letter-spacing: 0.5px;'>{clause_title}</strong>
            </div>
            """)
        elif stripped.startswith("# "):
            doc_heading = stripped[2:].strip()
            html_out.append(f"""
            <h2 style='color: #F8FAFC; text-align: center; margin: 15px 0 20px 0; font-family: Georgia, serif; border-bottom: 1px solid #334155; padding-bottom: 10px;'>
                {doc_heading}
            </h2>
            """)
        elif stripped.startswith("### "):
            sub_title = stripped[4:].strip()
            html_out.append(f"<h4 style='color: #93C5FD; margin: 10px 0 4px 10px; font-size: 13px;'>{sub_title}</h4>")
        elif stripped.startswith("- ") or stripped.startswith("* "):
            bullet_content = stripped[2:].strip()
            html_out.append(f"""
            <div style='display: flex; margin: 5px 0 5px 20px;'>
                <span style='color: #38BDF8; margin-right: 8px;'>•</span>
                <span style='color: #CBD5E1; font-size: 13px; line-height: 1.6;'>{bullet_content}</span>
            </div>
            """)
        elif re.match(r"^(\d+\.|\d+\.\d+|\([a-z]\))\s+", stripped):
            html_out.append(f"""
            <div style='margin: 6px 0 6px 12px; color: #E2E8F0; font-size: 13.5px; line-height: 1.6;'>
                <span style='font-weight: 600; color: #93C5FD;'>{stripped}</span>
            </div>
            """)
        elif "IN WITNESS WHEREOF" in stripped.upper() or "SIGNATURE" in stripped.upper():
            html_out.append(f"""
            <div style='margin-top: 25px; padding: 12px; background: rgba(30, 41, 59, 0.7); border: 1px dashed #475569; border-radius: 6px;'>
                <strong style='color: #F1F5F9; font-size: 13px;'>{stripped}</strong>
            </div>
            """)
        else:
            # Inline bold markdown conversion
            formatted_line = re.sub(r"\*\*(.*?)\*\*", r"<strong style='color: #F8FAFC;'>\1</strong>", stripped)
            html_out.append(f"<p style='margin: 6px 0; color: #CBD5E1; line-height: 1.65; font-size: 13.5px; text-align: justify;'>{formatted_line}</p>")
            
    return "\n".join(html_out)