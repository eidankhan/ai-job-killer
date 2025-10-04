from sqlalchemy.orm import Session
from app.models.skill_group import SkillGroup
from app.schemas.skillgroup import SkillGroupSchema

def insert_skillgroups(db: Session, skillgroups: list[SkillGroupSchema]):
    """
    Bulk insert skill groups into DB.
    """
    objects = [SkillGroup(**sg.dict()) for sg in skillgroups]
    db.bulk_save_objects(objects, return_defaults=False)
    db.commit()
