from fastapi import FastAPI
from app.api.routes import auth, documents, search, audit

app = FastAPI(title="RAG System")

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(documents.router, prefix="/documents", tags=["documents"])
app.include_router(search.router, prefix="/search", tags=["search"])
app.include_router(audit.router, prefix="/audit", tags=["audit"])

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

007219a6-1126-4b19-9df9-b9f770ffc12d