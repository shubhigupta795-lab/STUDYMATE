from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SpaceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None


class SpaceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    created_at: datetime


class SourceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    space_id: int
    source_type: str
    title: str
    filename: str | None
    created_at: datetime


class KnowledgePartitionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    space_id: int
    source_id: int
    partition: str
    item_index: int
    content: dict
    created_at: datetime
