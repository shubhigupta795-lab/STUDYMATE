from datetime import datetime
from pydantic import BaseModel


class SourceCreate(BaseModel):
    type: str  # 'doc', 'pdf', 'youtube', 'web'
    title: str
    url_or_path: str | None = None
    content: str | None = None


class SourceResponse(BaseModel):
    id: int
    space_id: int
    type: str
    title: str
    url_or_path: str | None = None
    content: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class SpaceCreate(BaseModel):
    name: str
    description: str | None = None


class SpaceResponse(BaseModel):
    id: int
    name: str
    description: str | None
    created_at: datetime
    sources: list[SourceResponse] = []

    class Config:
        from_attributes = True


class QueryRequest(BaseModel):
    query: str
    mode: str = "qa"  # 'qa', 'compare', 'gaps'


class QueryResponse(BaseModel):
    answer: str
    sources_used: list[str] = []