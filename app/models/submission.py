from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    widget_id = Column(Integer, ForeignKey("widgets.id", ondelete="CASCADE"), nullable=False, index=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    form_data = Column(JSON, nullable=False)
    ip_address = Column(String(45), nullable=True)
    country = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    status = Column(String(50), nullable=False, default="new")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    widget = relationship("Widget", back_populates="submissions")
    owner = relationship("User", back_populates="submissions")

    def __repr__(self):
        return f"<Submission {self.id} - Widget {self.widget_id}>"
