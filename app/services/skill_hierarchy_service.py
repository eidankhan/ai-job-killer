from sqlalchemy.orm import Session
from app.models.skill_hierarchy import SkillHierarchy
from app.schemas.skill_hierarchy import SkillHierarchySchema

def insert_skill_hierarchies(db: Session, skill_hierarchies: list[SkillHierarchySchema]):
    """
    Insert skill hierarchies into DB.
    Uses bulk save to improve performance.
    """
    db_objs = [SkillHierarchy(**sh.dict()) for sh in skill_hierarchies]
    db.bulk_save_objects(db_objs)
    db.commit()
