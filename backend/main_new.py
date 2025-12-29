"""
Tax Filing System Backend - Main Entry Point

FastAPI application with:
- PostgreSQL + pgvector for vector storage
- Microsoft AutoGen for AI agents
- Multi-provider LLM support (OpenAI, Anthropic, etc.)
- Local LLM support (optimized for 4GB VRAM)
- Async-first database operations
"""
import sys
import os
from pathlib import Path

# Add backend to path for imports
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from app.core.config import settings
from app.core.database import engine, Base, check_db_connection
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import time
import uvicorn

# Import API routers
from app.api import auth, users, tax_forms, sdui, ws, documents, filing, chat_llm

# ============================================================================
# Initialize Database
# ============================================================================
print("🔧 Initializing database...")
try:
    Base.metadata.create_all(bind=engine)
    if check_db_connection():
        print("✅ Database connected successfully")
    else:
        print("⚠️  Database connection failed - check your configuration")
except Exception as e:
    print(f"❌ Database initialization error: {e}")

# ============================================================================
# Initialize FastAPI App
# ============================================================================
app = FastAPI(
    title=settings.APP_NAME,
    description="Automated Indian tax filing system with AI agents",
    version=settings.APP_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    debug=settings.DEBUG,
)

# ============================================================================
# CORS Middleware
# ============================================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# ============================================================================
# Request Timing Middleware
# ============================================================================
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add X-Process-Time header to track request duration."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# ============================================================================
# Exception Handlers
# ============================================================================
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with detailed messages."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.errors(),
            "message": "Validation error - please check your input"
        }
    )

@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle database errors."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Database error occurred",
            "message": str(exc) if settings.DEBUG else "Internal database error"
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "message": str(exc) if settings.DEBUG else "An unexpected error occurred"
        }
    )

# ============================================================================
# API Routers
# ============================================================================
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(tax_forms.router, prefix="/api")
app.include_router(sdui.router)
app.include_router(ws.router, prefix="/api")
app.include_router(documents.router, prefix="/api")
app.include_router(filing.router, prefix="/api")
app.include_router(chat_llm.router, prefix="/api")

# ============================================================================
# Root Endpoints
# ============================================================================
@app.get("/")
async def root():
    """Root endpoint - API information."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "environment": settings.ENVIRONMENT,
        "docs": "/api/docs",
        "health": "/api/health"
    }

@app.get("/api/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    
    Returns:
        - status: API status
        - database: Database connection status
        - timestamp: Current server time
    """
    from datetime import datetime
    
    # Test database connection
    db_status = "healthy" if check_db_connection() else "unhealthy"
    
    return {
        "status": "healthy",
        "database": db_status,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.utcnow().isoformat()
    }

# ============================================================================
# Startup and Shutdown Events
# ============================================================================
@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    print("\n" + "="*70)
    print(f"🚀 {settings.APP_NAME} starting up...")
    print(f"📍 Environment: {settings.ENVIRONMENT}")
    print(f"🌐 API documentation: http://{settings.HOST}:{settings.PORT}/api/docs")
    print(f"❤️  Health check: http://{settings.HOST}:{settings.PORT}/api/health")
    print("="*70 + "\n")

@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    print(f"\n🛑 {settings.APP_NAME} shutting down...\n")

# ============================================================================
# Main Execution
# ============================================================================
def main():
    """Run the FastAPI application with uvicorn."""
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD and settings.is_development,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True,
    )

if __name__ == "__main__":
    main()
