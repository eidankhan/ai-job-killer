# app/models/skill.py
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base

class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    conceptType = Column(String(100))
    conceptUri = Column(Text, unique=True, nullable=False)
    skillType = Column(String(100))
    reuseLevel = Column(String(100))
    preferredLabel = Column(String(255))
    altLabels = Column(Text)
    hiddenLabels = Column(Text)
    status = Column(String(50))
    modifiedDate = Column(DateTime)
    scopeNote = Column(Text)
    definition = Column(Text)
    inScheme = Column(Text)
    description = Column(Text)

    occupations = relationship(
    "OccupationSkillRelation",
    back_populates="skill",
    cascade="all, delete-orphan"
)
