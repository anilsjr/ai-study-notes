from fastapi import APIRouter, File, UploadFile, Depends, HTTPException
from typing import Optional
from app.services.document_parser import DocumentParser
from app.vectorstore.chroma import vector_store
from app.agents.orchestrator import orchestrator
import uuid

router = APIRouter()

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    contents = await file.read()
    
    if file.filename.endswith(".pdf"):
        text = DocumentParser.parse_pdf(contents)
    elif file.filename.endswith(".docx"):
        text = DocumentParser.parse_docx(contents)
    elif file.filename.endswith(".txt"):
        text = contents.decode("utf-8")
    else:
        raise HTTPException(status_code=400, detail="Unsupported file format.")
    
    chunks = DocumentParser.chunk_text(text)
    collection_name = f"doc_{uuid.uuid4().hex[:12]}"
    
    # Normally we'd use an Embedding Agent or service via google-genai to embed these chunks.
    # For this architecture, Chroma default embeddings logic will be leveraged for simplicity internally
    # unless text/gemini is passed to a specific model mapping.
    
    vector_store.add_documents(
        collection_name=collection_name,
        texts=chunks,
        metadatas=[{"source": file.filename}] * len(chunks),
        ids=[f"chunk_{i}" for i in range(len(chunks))]
    )
    
    return {"message": "Document ingested", "collection_id": collection_name, "chunks_processed": len(chunks)}


@router.post("/notes/generate")
async def generate_study_pack(collection_id: str):
    # Fetch partial texts from chroma or use all (simplified here to fetch top content)
    results = vector_store.query(collection_id, query_text="summary of main points", n_results=10)
    context = "\n".join([doc for sublist in results['documents'] for doc in sublist])
    
    pack = await orchestrator.workflow_generate_study_pack(context)
    return {"study_pack": pack}


@router.post("/rag/ask")
async def ask_question(collection_id: str, query: str):
    answer = await orchestrator.workflow_rag_chat(collection_id, query)
    return {"answer": answer}
