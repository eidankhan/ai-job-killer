from sqlalchemy import Column, Integer, String, Text
from app.core.database import Base

class SkillHierarchy(Base):
    __tablename__ = "skill_hierarchies"

    id = Column(Integer, primary_key=True, autoincrement=True)

    level_0_uri = Column(String, index=True, nullable=True)
    level_0_preferred_term = Column(String, nullable=True)
    level_1_uri = Column(String, nullable=True)
    level_1_preferred_term = Column(String, nullable=True)
    level_2_uri = Column(String, nullable=True)
    level_2_preferred_term = Column(String, nullable=True)
    level_3_uri = Column(String, nullable=True)
    level_3_preferred_term = Column(String, nullable=True)

    description = Column(Text, nullable=True)
    scope_note = Column(Text, nullable=True)

    level_0_code = Column(String, nullable=True)
    level_1_code = Column(String, nullable=True)
    level_2_code = Column(String, nullable=True)
    level_3_code = Column(String, nullable=True)
