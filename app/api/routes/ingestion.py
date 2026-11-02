from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.services.ingestion_service import ingest_document, ingest_transcript, partitions_as_dict

router = APIRouter(prefix="/spaces", tags=["Ingestion"])


class TranscriptRequest(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    transcript: str = Field(min_length=1)


class IngestionResponse(BaseModel):
    space_id: int
    source_id: int
    knowledge_ids: list[int]
    source_type: str
    title: str
    partitions: dict[str, list[dict]]


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/{space_id}/ingest/document", response_model=IngestionResponse)
async def upload_document(
    space_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    filename = file.filename or "document"
    content = await file.read()
    try:
        source, knowledge_rows = ingest_document(db, space_id, filename, content)
        return IngestionResponse(
            space_id=space_id,
            source_id=source.id,
            knowledge_ids=[row.id for row in knowledge_rows],
            source_type=source.source_type,
            title=source.title,
            partitions=partitions_as_dict(knowledge_rows),
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Ingestion failed: {exc}") from exc


@router.post("/{space_id}/ingest/transcript", response_model=IngestionResponse)
def upload_transcript(
    space_id: int,
    request: TranscriptRequest,
    db: Session = Depends(get_db),
):
    try:
        source, knowledge_rows = ingest_transcript(
            db, space_id, request.title, request.transcript
        )
        return IngestionResponse(
            space_id=space_id,
            source_id=source.id,
            knowledge_ids=[row.id for row in knowledge_rows],
            source_type=source.source_type,
            title=source.title,
            partitions=partitions_as_dict(knowledge_rows),
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Ingestion failed: {exc}") from exc
