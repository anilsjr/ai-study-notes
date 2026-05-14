from dotenv import load_dotenv
load_dotenv()

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.document_routes import router as document_router
import time

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Pre-warm ADK runners on startup (imports trigger agent construction)
    from app import adk_runner  # noqa: F401
    yield

app = FastAPI(
    title="AI Study Notes with QA Generator",
    description="Backend API powered by Google ADK multi-agent system.",
    version="2.0.0",
    lifespan=lifespan,
)

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
    response.headers["X-Process-Time"] = str(time.time() - start_time)
    return response

@app.get("/")
async def root():
    return {"message": "Welcome to AI Study Notes & QA Generator API (ADK v2)"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "adk": "active"}

app.include_router(document_router, prefix="/api/v1")
