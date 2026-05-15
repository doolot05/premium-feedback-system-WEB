import datetime
from sqlalchemy import Column, Integer, String, DateTime
from database import Base

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    rating = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)