"""
Main FastAPI application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import auth, tax, explain

app = FastAPI(
    title="Tax Fluent Chat API",
    description="Backend API for adaptive tax assistance with progressive calculations and explainability",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(tax.router)
app.include_router(explain.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Tax Fluent Chat API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "auth": "/auth",
            "tax": "/tax",
            "explain": "/explain"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
