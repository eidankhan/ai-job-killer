from sqlalchemy.orm import Session
from app.models.skill import Skill
from app.schemas.skill import SkillSchema

def insert_skills(db: Session, skills: list[SkillSchema]):
    """
    Bulk insert skills into DB.
    """
    objects = [Skill(**skill.dict()) for skill in skills]
    db.bulk_save_objects(objects, return_defaults=False)
    db.commit()
