from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database.connection import Base


class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    space_id = Column(Integer, ForeignKey("spaces.id"), nullable=False)
    type = Column(String(50), nullable=False)  # 'doc', 'pdf', 'youtube', 'web'
    title = Column(String(255), nullable=False)
    url_or_path = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    space = relationship("Space", back_populates="sources")
