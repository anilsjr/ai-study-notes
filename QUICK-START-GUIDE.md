# Quick Start Guide

This guide gets AI Study Notes running in a few minutes.

## Prerequisites

- Python 3.12+
- Pip
- Docker Desktop (optional, for containerized run)
- A Gemini API key

## 1) Clone and Enter Project

```bash
git clone <your-repo-url>
cd ai-study-notes-app
```

## 2) Configure Environment

Create a local environment file from the example:

```bash
copy .env.example .env
```

Open `.env` and set:

- `GEMINI_API_KEY=your_real_key`

Recommended defaults can stay as-is:

- `DATABASE_URL=sqlite:///./study_notes.db`
- `CHROMA_DB_DIR=./chroma_data`

## 3) Install Dependencies

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 4) Start Backend API

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Verify health:

- `http://localhost:8000/health`
- `http://localhost:8000/docs`

## 5) Start Streamlit UI

In a new terminal:

```bash
.venv\Scripts\activate
streamlit run app_ui.py
```

Open:

- `http://localhost:8501`

## 6) First End-to-End Flow

1. In Streamlit, go to Knowledge Base / Notes Management.
2. Upload a PDF, DOCX, or TXT file.
3. Copy or note the generated collection ID.
4. Click Generate study pack.
5. Switch to AI Study Assistant mode and ask questions against that collection.

## API-Only Flow (No Streamlit)

### Upload file

```bash
curl -X POST "http://localhost:8000/api/v1/upload" -F "file=@sample.pdf"
```

### Generate study pack

```bash
curl -X POST "http://localhost:8000/api/v1/notes/generate?collection_id=<collection_id>"
```

### Ask question

```bash
curl -X POST "http://localhost:8000/api/v1/rag/ask?collection_id=<collection_id>&query=Explain+the+main+topic"
```

## Docker Quick Start

```bash
docker compose up --build
```

API docs will be available at:

- `http://localhost:8000/docs`

## Troubleshooting

- Backend offline in Streamlit:
  - Ensure Uvicorn is running on port 8000.
  - Set `AI_STUDY_API_BASE_URL` if backend is on another host/port.

- Upload works but generation fails:
  - Check `GEMINI_API_KEY` in `.env`.
  - Inspect backend logs for ADK/Gemini errors.

- Chroma issues:
  - Ensure `CHROMA_DB_DIR` exists and is writable.

- Slow responses:
  - Increase `AI_STUDY_API_TIMEOUT_SECONDS` for large documents.

## What Is Implemented Today

- FastAPI endpoints for upload, study pack generation, and RAG question-answering
- ADK-based agents (notes, MCQ, flashcards, RAG)
- Streamlit frontend with collection management and chat

## What Is Not Fully Wired Yet

- A dedicated automated tests folder in this repo
- PDF export endpoint wiring in the current FastAPI router
