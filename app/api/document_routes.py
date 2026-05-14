from fastapi import APIRouter, File, UploadFile, HTTPException
from app.services.document_parser import DocumentParser
from app.vectorstore.chroma import vector_store
from app.adk_runner import run_study_pack, run_rag_chat
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
    vector_store.add_documents(
        collection_name=collection_name,
        texts=chunks,
        metadatas=[{"source": file.filename}] * len(chunks),
        ids=[f"chunk_{i}" for i in range(len(chunks))],
    )
    return {"message": "Document ingested", "collection_id": collection_name, "chunks_processed": len(chunks)}


@router.post("/notes/generate")
async def generate_study_pack(collection_id: str):
    results = vector_store.query(collection_id, query_text="summary of main points", n_results=10)
    context = "\n".join([doc for sublist in results["documents"] for doc in sublist])
    session_id = f"study_pack_{collection_id}"
    pack = await run_study_pack(context, session_id=session_id)
    return {"study_pack": pack}


@router.post("/rag/ask")
async def ask_question(collection_id: str, query: str):
    # Use collection_id as part of session_id to maintain per-collection chat history
    session_id = f"rag_{collection_id}"
    answer = await run_rag_chat(collection_id, query, session_id=session_id)
    return {"answer": answer}
