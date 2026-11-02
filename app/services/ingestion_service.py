import json
import tempfile
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from app.llm.gemini import create_embedding, extract_from_pdf, extract_from_text
from app.models.knowledge import KnowledgePartition
from app.models.source import Source
from app.models.space import Space
from app.parsers.docx_parser import parse_docx
from app.parsers.pdf_parser import extract_pdf_text

MAX_FILE_BYTES = 10 * 1024 * 1024
ALLOWED_DOCUMENTS = {".docx": "docx", ".pdf": "pdf"}


def _validate_space(db: Session, space_id: int) -> Space:
    space = db.get(Space, space_id)
    if not space:
        raise LookupError(f"Space {space_id} does not exist.")
    return space


def _item_to_content(item: Any) -> dict:
    if hasattr(item, "model_dump"):
        return item.model_dump()
    return {"value": item}


def _partition_rows(extraction: Any) -> list[tuple[str, int, dict]]:
    """Turn the structured LLM response into the predefined Space partitions."""
    data = extraction.model_dump()
    rows: list[tuple[str, int, dict]] = []

    list_partitions = {
        "key_concepts",
        "methodology",
        "findings",
        "important_facts",
        "claims",
        "limitations",
        "what_they_could_not_establish",
        "what_can_be_done_better",
        "potentially_overlooked",
        "practical_implications",
        "open_research_questions",
        "fresh_knowledge",
        "important_references",
    }

    for partition, value in data.items():
        if partition in {"title", "summary", "research_problem", "research_objective", "novelty"}:
            if value not in (None, ""):
                rows.append((partition, 0, {"value": value}))
            continue

        if partition in list_partitions:
            for index, item in enumerate(value or []):
                rows.append((partition, index, _item_to_content(item)))

    return rows


def _store_extraction(
    db: Session,
    *,
    space_id: int,
    source: Source,
    extraction: Any,
) -> list[KnowledgePartition]:
    partitions = _partition_rows(extraction)
    stored: list[KnowledgePartition] = []

    for partition, item_index, content in partitions:
        embedding_text = json.dumps(
            {"partition": partition, "content": content},
            ensure_ascii=False,
            separators=(",", ":"),
        )
        row = KnowledgePartition(
            space_id=space_id,
            source_id=source.id,
            partition=partition,
            item_index=item_index,
            content=content,
            embedding=create_embedding(embedding_text),
        )
        db.add(row)
        stored.append(row)

    return stored


def partitions_as_dict(rows: list[KnowledgePartition]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {}
    for row in rows:
        grouped.setdefault(row.partition, []).append(row.content)
    return grouped


def ingest_document(db: Session, space_id: int, filename: str, content: bytes):
    _validate_space(db, space_id)

    if len(content) > MAX_FILE_BYTES:
        raise ValueError("File is larger than the 10 MB V1 limit.")

    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_DOCUMENTS:
        raise ValueError("Only DOCX and PDF files are supported in V1.")

    source_type = ALLOWED_DOCUMENTS[suffix]
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(content)
            temp_path = Path(tmp.name)

        if source_type == "docx":
            raw_text, metadata = parse_docx(temp_path)
            extraction, grounding = extract_from_text(raw_text)
        else:
            raw_text, metadata = extract_pdf_text(temp_path)
            extraction, grounding = extract_from_pdf(temp_path)

        metadata = {**metadata, **grounding}
        source = Source(
            space_id=space_id,
            source_type=source_type,
            title=extraction.title or Path(filename).stem,
            filename=filename,
            raw_text=raw_text,
            source_metadata=metadata,
        )
        db.add(source)
        db.flush()

        stored = _store_extraction(
            db, space_id=space_id, source=source, extraction=extraction
        )
        db.commit()
        db.refresh(source)
        for row in stored:
            db.refresh(row)
        return source, stored
    except Exception:
        db.rollback()
        raise
    finally:
        if temp_path:
            temp_path.unlink(missing_ok=True)


def ingest_transcript(db: Session, space_id: int, title: str, transcript: str):
    _validate_space(db, space_id)
    if not transcript.strip():
        raise ValueError("Transcript cannot be empty.")
    if len(transcript.encode("utf-8")) > MAX_FILE_BYTES:
        raise ValueError("Transcript is larger than the 10 MB V1 limit.")

    extraction, grounding = extract_from_text(transcript)
    source = Source(
        space_id=space_id,
        source_type="transcript",
        title=extraction.title or title,
        filename=None,
        raw_text=transcript,
        source_metadata=grounding,
    )
    db.add(source)
    db.flush()

    stored = _store_extraction(
        db, space_id=space_id, source=source, extraction=extraction
    )
    db.commit()
    db.refresh(source)
    for row in stored:
        db.refresh(row)
    return source, stored
