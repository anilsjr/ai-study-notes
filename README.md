# AI Study Notes with QA Generator

AI-powered study assistant using FastAPI, Google ADK agents, ChromaDB, and Gemini.

For the fastest setup path, start with [QUICK-START-GUIDE.md](./QUICK-START-GUIDE.md).

This repository currently contains:

- A FastAPI backend for document upload, study-pack generation, and RAG chat
- A Streamlit frontend for document management and AI study assistant chat
- ADK-based agents for summary, MCQ, flashcard, and retrieval-augmented answers

## What It Does

- Upload PDF, DOCX, and TXT files
- Chunk and store document text in ChromaDB
- Generate a study pack:
	- Summary (markdown)
	- MCQs (JSON)
	- Flashcards (JSON)
- Ask questions against an indexed collection with RAG

## Tech Stack

- Python 3.12+
- FastAPI + Uvicorn
- Google ADK (`google-adk`)
- Gemini model family (`gemini-2.5-flash` in current agents)
- ChromaDB persistent vector store
- Streamlit frontend

## Current Architecture

### Backend entrypoint

- `app/main.py`
	- Registers API routes under `/api/v1`
	- Exposes health endpoint at `/health`
	- Enables permissive CORS for local development
	- Pre-warms ADK runners in app lifespan

### API routes

- `app/api/document_routes.py`
	- `POST /api/v1/upload`
	- `POST /api/v1/notes/generate?collection_id=...`
	- `POST /api/v1/rag/ask?collection_id=...&query=...`

### ADK runners and agents

- `app/adk_runner.py`
	- `study_pack_runner`: runs study pack pipeline
	- `rag_runner`: runs RAG chat pipeline
- `app/agents/orchestrator.py`
	- `study_pack_agent`: `ParallelAgent` combining notes + MCQ + flashcard agents
	- `rag_orchestrator`: direct RAG agent
- `app/agents/notes_agent.py`
	- Produces summary markdown (`output_key="summary"`)
- `app/agents/qa_agent.py`
	- Produces MCQs (`output_key="mcqs"`) and flashcards (`output_key="flashcards"`)
- `app/agents/rag_agent.py`
	- Uses `retrieve_context` tool to query Chroma collection and answer from notes only

### Data layer

- `app/services/document_parser.py`
	- Extracts text from PDF/DOCX/TXT and chunks text
- `app/vectorstore/chroma.py`
	- Chroma persistent client and collection operations

### Frontend

- `app_ui.py`
	- Streamlit UI with two modes:
		- Knowledge Base / Notes Management
		- AI Study Assistant

## Environment Variables

Copy `.env.example` to `.env` and set at least:

- `GEMINI_API_KEY` (required for ADK/Gemini generation)
- `DATABASE_URL` (defaults to SQLite)
- `CHROMA_DB_DIR` (defaults to `./chroma_data`)

Optional Streamlit client variables:

- `AI_STUDY_API_BASE_URL` (default: `http://localhost:8000`)
- `AI_STUDY_API_PREFIX` (default: `/api/v1`)
- `AI_STUDY_API_TIMEOUT_SECONDS` (default: `180`)

## Run Locally (FastAPI + Streamlit)

1. Create and activate a virtual environment.
2. Install dependencies:

	 `pip install -r requirements.txt`

3. Create environment file:

	 `copy .env.example .env` (Windows)

4. Start backend:

	 `uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`

5. In another terminal, start Streamlit UI:

	 `streamlit run app_ui.py`

6. Open:

- API docs: `http://localhost:8000/docs`
- Streamlit UI: `http://localhost:8501`

## Run with Docker

`docker compose up --build`

By default this starts the FastAPI service on `http://localhost:8000`.

## API Quick Examples

### Upload a document

```bash
curl -X POST "http://localhost:8000/api/v1/upload" \
	-F "file=@sample.pdf"
```

### Generate study pack

```bash
curl -X POST "http://localhost:8000/api/v1/notes/generate?collection_id=doc_abc123"
```

### Ask RAG question

```bash
curl -X POST "http://localhost:8000/api/v1/rag/ask?collection_id=doc_abc123&query=What+is+the+main+idea%3F"
```

## Project Layout (tracked files)

```
.
|- app/
|  |- agents/
|  |- api/
|  |- core/
|  |- db/
|  |- models/
|  |- services/
|  |- vectorstore/
|  |- adk_runner.py
|  |- main.py
|- app_ui.py
|- docker-compose.yml
|- Dockerfile
|- requirements.txt
|- .env.example
```

## Notes

- The repository currently does not include a dedicated automated test suite.
- `export_agent.py` contains PDF generation tooling, but export routes are not yet wired into the current FastAPI router.
