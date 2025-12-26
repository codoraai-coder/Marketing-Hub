from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from app.database import supabase
from app.routers import workspace, workflow, job, generation, content, posting

# Load environment variables
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 MCP Hub Backend starting...")
    print(f"✅ Connected to Supabase: {os.getenv('SUPABASE_URL')}")
    yield
    # Shutdown
    print("👋 MCP Hub Backend shutting down...")


# Create FastAPI app
app = FastAPI(
    title="MCP Hub API",
    description="Master Control Program - Marketing Hub Backend",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(workspace.router, prefix="/api/workspaces", tags=["workspaces"])
app.include_router(workflow.router, prefix="/api/workflows", tags=["workflows"])
app.include_router(job.router, prefix="/api/jobs", tags=["jobs"])
app.include_router(content.router, prefix="/api/content", tags=["content"])
app.include_router(posting.router)
app.include_router(generation.router, prefix="/api/v1", tags=["generation"])


@app.get("/")
async def root():
    return {
        "message": "🎯 Master Control Program API",
        "status": "active",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 3000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
