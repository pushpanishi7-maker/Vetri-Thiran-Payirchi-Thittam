#!/bin/bash
# Activate virtual environment if present
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run backend in background
uvicorn legalEaseAPI.main:app --host 127.0.0.1 --port 8000 --reload &
BACKEND_PID=$!

# Run Streamlit frontend
streamlit run frontend/app.py

# Terminate backend on exit
kill $BACKEND_PID