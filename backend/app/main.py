"""FastAPI main application."""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import time

from app.core.database import engine, Base
from app.api import auth, users, tax_forms, sdui, ws, documents, filing, chat_llm

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Tax Filing System API",
    description="Automated tax filing system with mode-based question flows",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
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
app.include_router(chat_llm.router, prefix="/api")  # LLaMA Chat API

# ============================================================================
# CORS Middleware
# ============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
            "message": str(exc)
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "message": str(exc)
        }
    )
@app.get("/")
async def root():
    """Root endpoint - API information."""
    return {
        "name": "Tax Filing System API",
        "version": "1.0.0",
        "status": "running",
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
    from app.core.database import SessionLocal
    from datetime import datetime
    from sqlalchemy import text
    
    # Test database connection
    db_status = "healthy"
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    return {
        "status": "healthy",
        "database": db_status,
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================================================
# Startup and Shutdown Events
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    print("Tax Filing System API starting up...")
    print("API documentation available at: http://localhost:8000/api/docs")
    print("Health check available at: http://localhost:8000/api/health")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    print("Tax Filing System API shutting down...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
