# app/models/occupation.py
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base

class Occupation(Base):
    __tablename__ = "occupations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    conceptType = Column(String(50))
    conceptUri = Column(Text, unique=True, nullable=False)
    iscoGroup = Column(String(50))
    preferredLabel = Column(String(255))
    altLabels = Column(Text)
    hiddenLabels = Column(Text)
    status = Column(String(50))
    modifiedDate = Column(DateTime)
    regulatedProfessionNote = Column(Text)
    scopeNote = Column(Text)
    definition = Column(Text)
    inScheme = Column(Text)
    description = Column(Text)
    code = Column(String(50))

    skills = relationship(
    "OccupationSkillRelation",
    back_populates="occupation",
    cascade="all, delete-orphan"
)
