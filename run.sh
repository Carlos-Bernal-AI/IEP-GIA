#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
unset GEMINI_API_KEY
streamlit run app.py
