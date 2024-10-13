from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db import Base

class UserOAuth(Base):
    __tablename__ = "user_oauth"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    oauth_provider = Column(String, nullable=False)
    oauth_user_id = Column(String, nullable=False)

    user = relationship("User", back_populates="oauth_providers")

    __table_args__ = (UniqueConstraint("user_id", "oauth_provider"),)
