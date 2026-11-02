from fastapi import FastAPI
from fastapi.responses import FileResponse
from sqlalchemy import text

from app.api.routes.ingestion import router as ingestion_router
from app.api.routes.spaces import router as spaces_router
from app.database.connection import Base, engine
from app.models import KnowledgePartition, Source, Space


app = FastAPI(
    title="STUDYMATE",
    description="AI research workspace: source ingestion and structured research knowledge extraction.",
    version="1.0.0",
)


def initialize_database() -> None:
    with engine.begin() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    Base.metadata.create_all(bind=engine)


initialize_database()
app.include_router(spaces_router)
app.include_router(ingestion_router)


@app.get("/", include_in_schema=False)
def root():
    return FileResponse("app/static/index.html")


@app.get("/api", include_in_schema=False)
def api_info():
    return {
        "message": "STUDYMATE API is running",
        "docs": "/docs",
        "supported_inputs": ["docx", "pdf", "transcript"],
        "max_file_size_mb": 10,
    }


@app.get("/health")
def health():
    return {"status": "healthy"}
