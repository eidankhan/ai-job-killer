from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class OccupationSkillRelation(Base):
    __tablename__ = "occupation_skill_relations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    occupation_id = Column(Integer, ForeignKey("occupations.id", ondelete="CASCADE"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)

    relationType = Column(String(50))
    skillType = Column(String(100))

    # Relationships
    occupation = relationship("Occupation", back_populates="skills")
    skill = relationship("Skill", back_populates="occupations")
