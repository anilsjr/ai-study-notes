# AI Study Notes with QA Generator 2025

An AI-powered study assistant backend application utilizing Google ADK, FastAPI, ChromaDB, and Gemini API.

## Features

- **Document Ingestion**: Upload PDFs, DOCX, and TXT files.
- **RAG QA**: Chat with your study materials.
- **Notes Generation**: Summaries, key concepts, formulas.
- **QA Generator**: MCQs, Flashcards, short/long answers.
- **PDF Export**: Download beautiful formatted study modules.

## Architecture

This project is built using a multi-agent architecture with Google ADK:

- `OrchestratorAgent`: Routes user requests to appropriate sub-agents.
- `DocumentIngestionAgent`: Handles parsing and chunking.
- `EmbeddingAgent`: Stores and manages ChromaDB vectors.
- `NotesGenerationAgent`: Produces structured notes via Gemini.
- `QAGenerationAgent`: Generates structured questions/flashcards.
- `RAGQueryAgent`: Performs RAG to answer queries.
- `PDFExportAgent`: Compiles exported PDFs.

## Setup

1. Copy `.env.example` to `.env` and fill the variables.
2. Run via Docker Compose: `docker-compose up --build`
3. Access API at `http://localhost:8000/docs`
