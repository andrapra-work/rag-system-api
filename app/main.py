from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import auth, documents, search, bulk_upload  # Add bulk_upload import
from app.config import get_settings
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

settings = get_settings()

# Initialize FastAPI app
app = FastAPI(
    title="RAG System",
    description="Retrieval Augmented Generation System with Multi-tenant Support",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with proper tags and prefixes
app.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

app.include_router(
    documents.router,
    prefix="/documents",
    tags=["Document Management"]
)

app.include_router(
    search.router,
    prefix="/search",
    tags=["Search & RAG"]
)

app.include_router(
    bulk_upload.router,
    prefix="/upload",
    tags=["Bulk Upload"]
)

@app.get("/health", tags=["Health Check"])
async def health_check():
    """
    Health check endpoint to verify service status
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }

@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with API information
    """
    return {
        "app_name": "RAG System",
        "version": "1.0.0",
        "docs_url": "/docs",
        "health_check": "/health"
    }

# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logging.error(f"Global error handler: {str(exc)}")
    return {
        "status": "error",
        "message": str(exc),
        "path": request.url.path
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    logging.info("Starting up RAG System...")
    # Add any startup initialization here

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logging.info("Shutting down RAG System...")
    # Add any cleanup code here