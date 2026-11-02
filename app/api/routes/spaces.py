from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.models.knowledge import KnowledgePartition
from app.models.source import Source
from app.models.space import Space
from app.schemas import KnowledgePartitionResponse, SourceResponse, SpaceCreate, SpaceResponse

router = APIRouter(prefix="/spaces", tags=["Spaces"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("", response_model=SpaceResponse, status_code=status.HTTP_201_CREATED)
def create_space(space: SpaceCreate, db: Session = Depends(get_db)):
    new_space = Space(name=space.name, description=space.description)
    db.add(new_space)
    db.commit()
    db.refresh(new_space)
    return new_space


@router.get("", response_model=list[SpaceResponse])
def list_spaces(db: Session = Depends(get_db)):
    return db.query(Space).order_by(Space.created_at.desc()).all()


@router.get("/{space_id}", response_model=SpaceResponse)
def get_space(space_id: int, db: Session = Depends(get_db)):
    space = db.get(Space, space_id)
    if not space:
        raise HTTPException(status_code=404, detail="Space not found")
    return space


@router.get("/{space_id}/sources", response_model=list[SourceResponse])
def list_sources(space_id: int, db: Session = Depends(get_db)):
    if not db.get(Space, space_id):
        raise HTTPException(status_code=404, detail="Space not found")
    return (
        db.query(Source)
        .filter(Source.space_id == space_id)
        .order_by(Source.created_at.desc())
        .all()
    )


@router.get("/{space_id}/knowledge", response_model=list[KnowledgePartitionResponse])
def list_knowledge(space_id: int, db: Session = Depends(get_db)):
    if not db.get(Space, space_id):
        raise HTTPException(status_code=404, detail="Space not found")
    return (
        db.query(KnowledgePartition)
        .filter(KnowledgePartition.space_id == space_id)
        .order_by(
            KnowledgePartition.partition,
            KnowledgePartition.source_id,
            KnowledgePartition.item_index,
        )
        .all()
    )
