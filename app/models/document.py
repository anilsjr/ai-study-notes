from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    filename = Column(String)
    file_type = Column(String)
    chroma_collection_id = Column(String, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")
