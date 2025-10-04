from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, func, Index
from sqlalchemy.orm import relationship
from app.core.database import Base

class EmailVerification(Base):
    __tablename__ = "tb_email_verifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    code = Column(String(6), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    consumed = Column(Boolean, default=False)
    attempts = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="email_verifications")

Index("ix_email_verifications_user_active", EmailVerification.user_id, EmailVerification.consumed)
