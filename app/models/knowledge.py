from datetime import datetime, timezone

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base

EMBEDDING_DIMENSIONS = 768


class KnowledgePartition(Base):
    """One stored piece of extracted knowledge in a named Space partition."""

    __tablename__ = "knowledge_partitions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    space_id: Mapped[int] = mapped_column(
        ForeignKey("spaces.id", ondelete="CASCADE"), nullable=False, index=True
    )
    source_id: Mapped[int] = mapped_column(
        ForeignKey("sources.id", ondelete="CASCADE"), nullable=False, index=True
    )
    partition: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    item_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    content: Mapped[dict] = mapped_column(JSONB, nullable=False)
    embedding = mapped_column(Vector(EMBEDDING_DIMENSIONS), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    source = relationship("Source", back_populates="knowledge_partitions")
