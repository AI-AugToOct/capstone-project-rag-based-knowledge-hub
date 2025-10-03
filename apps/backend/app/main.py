"""
FastAPI Application Entry Point

This is the main file that creates and configures the FastAPI app.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

# Uncomment when routes are implemented:
# from app.api.routes import search, docs
# from app.db.client import init_db_pool, close_db_pool


# Create FastAPI app
app = FastAPI(
    title="RAG Knowledge Hub API",
    description="Permission-aware search API with vector embeddings and LLM-generated answers",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI at http://localhost:8000/docs
    redoc_url="/redoc"  # ReDoc at http://localhost:8000/redoc
)


# Configure CORS (Cross-Origin Resource Sharing)
# Allows frontend (http://localhost:3000) to call backend (http://localhost:8000)
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,  # Which origins can call this API
    allow_credentials=True,       # Allow cookies/auth headers
    allow_methods=["*"],          # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],          # Allow all headers
)


# Startup event: Initialize database connection pool
@app.on_event("startup")
async def startup():
    """
    Runs when the application starts.

    What This Does:
        - Initializes the database connection pool
        - Pool is reused across all requests (efficient!)

    Why We Need This:
        - Database connections are slow to create (~50-100ms)
        - Connection pool maintains 10-20 open connections
        - Requests reuse connections from pool (~1ms)

    Example Output:
        🚀 Starting RAG Knowledge Hub API...
        ✅ Database connection pool initialized
    """
    print("🚀 Starting RAG Knowledge Hub API...")

    # Uncomment when db/client.py is implemented:
    # await init_db_pool()
    # print("✅ Database connection pool initialized")

    raise NotImplementedError("TODO: Implement startup (initialize DB pool)")


# Shutdown event: Close database connection pool
@app.on_event("shutdown")
async def shutdown():
    """
    Runs when the application shuts down.

    What This Does:
        - Closes all connections in the pool
        - Frees up database resources

    Why We Need This:
        - Clean shutdown is important
        - Prevents connection leaks
        - Database can properly close connections

    Example Output:
        🛑 Shutting down RAG Knowledge Hub API...
        ✅ Database connection pool closed
    """
    print("🛑 Shutting down RAG Knowledge Hub API...")

    # Uncomment when db/client.py is implemented:
    # await close_db_pool()
    # print("✅ Database connection pool closed")

    raise NotImplementedError("TODO: Implement shutdown (close DB pool)")


# Include API routes
# Uncomment when routes are implemented:
# app.include_router(search.router, prefix="/api", tags=["Search"])
# app.include_router(docs.router, prefix="/api", tags=["Documents"])


# Health check endpoint (for monitoring)
@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.

    Returns:
        {"status": "healthy"}

    Why We Need This:
        - Load balancers need to check if service is alive
        - Monitoring systems ping this endpoint
        - Helps with rolling deployments (wait until healthy)

    Example Usage:
        curl http://localhost:8000/health
        {"status": "healthy"}
    """
    return {"status": "healthy"}


# Root endpoint (welcome message)
@app.get("/")
async def root():
    """
    Root endpoint - displays welcome message.

    Returns:
        Information about the API

    Example:
        curl http://localhost:8000/
        {
            "message": "RAG Knowledge Hub API",
            "docs": "http://localhost:8000/docs"
        }
    """
    return {
        "message": "RAG Knowledge Hub API",
        "version": "1.0.0",
        "docs": "http://localhost:8000/docs",
        "endpoints": {
            "search": "POST /api/search",
            "get_doc": "GET /api/docs/:doc_id",
            "health": "GET /health"
        }
    }


# Running the Application:
#
# Development (with auto-reload):
#   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
#
# Production:
#   uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
#
# Docker:
#   CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]


# API Documentation:
#
# Once the server is running, visit:
# - Swagger UI: http://localhost:8000/docs
#   → Interactive API testing (try endpoints in browser)
# - ReDoc: http://localhost:8000/redoc
#   → Alternative API documentation view


# CORS Explained:
#
# Without CORS middleware, this error would occur:
#
#   Frontend (http://localhost:3000) tries to call:
#   POST http://localhost:8000/api/search
#
#   Browser blocks request:
#   "Access to fetch at 'http://localhost:8000/api/search' from origin
#   'http://localhost:3000' has been blocked by CORS policy"
#
# CORS middleware tells browser:
#   "Yes, localhost:3000 is allowed to call this API"


# Environment Variables:
#
# Required:
#   - DATABASE_URL: PostgreSQL connection string
#   - SUPABASE_JWT_SECRET: For verifying JWTs
#   - COHERE_API_KEY: For embeddings and reranking
#   - GROQ_API_KEY: For LLM inference
#   - CORS_ORIGINS: Comma-separated allowed origins
#
# Example .env file:
#   DATABASE_URL=postgresql://user:pass@host:5432/db
#   SUPABASE_JWT_SECRET=your-secret
#   COHERE_API_KEY=your-key
#   GROQ_API_KEY=gsk_your-key
#   CORS_ORIGINS=http://localhost:3000,https://yourapp.com


# Logging (optional enhancement):
#
# import logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)
#
# @app.middleware("http")
# async def log_requests(request: Request, call_next):
#     logger.info(f"{request.method} {request.url.path}")
#     response = await call_next(request)
#     logger.info(f"Status: {response.status_code}")
#     return response