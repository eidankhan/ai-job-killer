from sqlalchemy import Column, String, Text, DateTime, Integer
from app.core.database import Base

class SkillGroup(Base):
    __tablename__ = "skill_groups"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    conceptType = Column(String(100))
    conceptUri = Column(Text, unique=True, nullable=False)
    preferredLabel = Column(String(255))
    altLabels = Column(Text)
    hiddenLabels = Column(Text)
    status = Column(String(50))
    modifiedDate = Column(DateTime) 
    scopeNote = Column(Text)
    inScheme = Column(Text)
    description = Column(Text)
    code = Column(String(50))
