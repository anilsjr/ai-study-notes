from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.document_routes import router as document_router
import time

app = FastAPI(
    title="AI Study Notes with QA Generator",
    description="Backend API for AI-powered study materials, flashcards, MCQs, and RAG capabilities.",
    version="1.0.0",
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_process_time_header(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

@app.get("/")
async def root():
    return {"message": "Welcome to AI Study Notes & QA Generator API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

app.include_router(document_router, prefix="/api/v1")
