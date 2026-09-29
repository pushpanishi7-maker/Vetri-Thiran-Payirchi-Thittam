# ⚖️ LegalEase – AI-Powered Legal Document Generator

> **Bridging the accessibility gap in legal services through the power of artificial intelligence.**

LegalEase is a modern, robust web application that simplifies the creation of legal documents by providing customizable, accurate, and editable templates. By leveraging advanced Generative AI (Google Gemini 1.5 Pro) and privacy-first local models (Meta LLaMA 3), users can instantly draft employment contracts, lease agreements, NDAs, and more, exporting them directly into formally structured PDF files.

---

## 🌟 Key Features

- **🧠 Dual AI Engine System:**
  - **Cloud Mode:** Uses Google Gemini 1.5 Pro for blazing-fast, highly contextual legal document generation.
  - **Offline Mode:** Uses local Meta LLaMA 3 (via Ollama) for complete privacy and air-gapped security. No internet required.
- **📝 Dynamic Editable Previews:** Review and manually amend AI-generated contracts directly in the browser before finalization.
- **📜 State-Preserving History:** Seamlessly switch between previously generated documents in your active session without losing data.
- **📕 Formal PDF Export:** Automatically compiles generated markdown into legally formatted PDFs featuring standard 1-inch margins, Times New Roman typography, embedded corporate logos, and paginated footers.
- **🔌 Decoupled Architecture:** High-performance FastAPI backend communicating with a responsive, interactive Streamlit frontend.

---

## 🛠️ Technology Stack

- **Frontend:** [Streamlit](https://streamlit.io/)
- **Backend:** [FastAPI](https://fastapi.tiangolo.com/), Uvicorn, Pydantic
- **AI Integration:** `google-generativeai` (Gemini), `requests` (Ollama/LLaMA 3)
- **Document Formatting:** `fpdf2` (PDF Generation)
- **Environment Management:** `python-dotenv`

---

## ⚙️ Prerequisites

Before you begin, ensure you have met the following requirements:

1. **Python 3.10+** installed on your machine.
2. **Git** installed (for cloning and version control).
3. *(Optional but Recommended)* **[Ollama](https://ollama.com/)** installed to run LLaMA 3 locally.
4. *(Optional)* A **[Google AI Studio API Key](https://aistudio.google.com/)** for using the Gemini Cloud engine.

---

## 🚀 Installation & Setup

**1. Clone the repository**

```bash
git clone https://github.com/pushpanishi7-maker/Vetri-Thiran-Payirchi-Thittam.git
cd Vetri-Thiran-Payirchi-Thittam
```

**2. Create and activate a virtual environment**

*Windows:*

```bash
python -m venv venv
venv\Scripts\activate
```

*macOS / Linux:*

```bash
python3 -m venv venv
source venv/bin/activate
```

**3. Install dependencies**

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**4. Generate default branding assets**

*(Run this once to create the placeholder logos required for PDF generation)*

```bash
python create_assets.py
```

---

## 🔑 Configuration (.env)

Create a `.env` file in the root directory and add your configurations. You can copy the provided `.env.example` file.

```env
# Google Gemini API Key from Google AI Studio
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-1.5-pro

# Local Offline LLaMA 3 (Ollama)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3

# API Backend Configuration
BACKEND_HOST=127.0.0.1
BACKEND_PORT=8000
```

> **Note:** You can also input your Gemini API Key dynamically via the Streamlit sidebar during runtime.

---

## 💻 Running the Application

### Option A: Single-Terminal Unified Launcher (Recommended)

If you have configured the unified launcher script:

```bash
# Windows
python run.py

# Or use the batch file directly
.\run.bat
```

### Option B: Manual Two-Terminal Setup

**Terminal 1: Start the FastAPI Backend**

```bash
uvicorn legalEaseAPI.main:app --reload --host 127.0.0.1 --port 8000
```

API documentation available at: `http://127.0.0.1:8000/docs`

**Terminal 2: Start the Streamlit Frontend**

```bash
streamlit run frontend/app.py
```

Web application available at: `http://localhost:8501`

---

## 📖 Usage Guide

1. **Select Engine:** Open the web app and use the left sidebar to select either **Google Gemini** or **Meta LLaMA 3**.
2. *(If LLaMA 3 is selected)* Ensure Ollama is running in the background via your system terminal (`ollama run llama3`).
3. **Input Parameters:** Fill in the Document Type, Parties Involved, Terms & Conditions, and Effective Date.
4. **Generate:** Click "Generate Document". Real-time logs will display in the backend terminal.
5. **Review & Edit:** Read the generated HTML preview. Click "Edit Document Content" to manually adjust clauses.
6. **Export:** Click the **"Export as Official PDF"** button to download your finalized, legally formatted document.

---

## 📁 Project Structure

```text
LEGALEASE/
│
├── ai_core/                    # AI integration and generation modules
│   ├── gemini_generator.py     # Google Gemini API integration
│   ├── llama_generator.py      # Local Ollama LLaMA 3 integration
│   └── generator.py            # Routing logic and PDF compilation
│
├── frontend/                   # User Interface layer
│   └── app.py                  # Streamlit web application
│
├── legalEaseAPI/               # Backend API layer
│   ├── main.py                 # FastAPI application initialization
│   └── routes.py               # API endpoints and Pydantic validation
│
├── Image/                      # Branding and UI assets
│   ├── Logo.png
│   └── inverseLogo.png
│
├── .env                        # Environment variables (Git-ignored)
├── .gitignore                  # Git tracking exclusions
├── config.py                   # Centralized configuration mapping
├── create_assets.py            # Utility script for placeholder generation
├── requirements.txt            # Python package dependencies
├── run.bat                     # Windows startup script
├── run.sh                      # Unix startup script
└── run.py                      # Unified startup launcher
```

---

## 📄 License & Disclaimer

**Disclaimer:** *LegalEase is an AI-powered tool designed to assist in the drafting of standard procedural agreements. It does not constitute formal legal advice. It is highly recommended to have complex or high-stakes legal documents reviewed by a qualified attorney prior to execution.*
