from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config.settings import settings
from src.utils.logger import export_logger as logger
from src.api.routers import auth, ingestion, pipeline, llm

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Enterprise Data Intelligence Platform API handling multi-format ingestion, quality validation, Medallion ETL, and LLM intelligence.",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enterprise CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(auth.router)
app.include_router(ingestion.router)
app.include_router(pipeline.router)
app.include_router(llm.router)


@app.get("/health", tags=["System Health"])
async def health_check():
    """System Health Check Endpoint for Kubernetes & Load Balancer probes."""
    return {
        "status": "HEALTHY",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)
