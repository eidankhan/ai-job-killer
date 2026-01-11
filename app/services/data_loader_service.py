"""
Business logic for loading data into specific schemas.
"""
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Type

# Import your SQLAlchemy Models
# Ensure these models do NOT have __table_args__ = {'schema': 'public'}
from app.models.occupation import Occupation
from app.models.skill import Skill
from app.models.skill_group import SkillGroup
from app.models.skill_hierarchy import SkillHierarchy
from app.models.occupation_skill_relation import OccupationSkillRelation

# Import Pydantic Schemas (Data Transfer Objects)

def _bulk_insert_with_schema(db: Session, objects: List[any], schema: str):
    """
    Private Helper: Sets the search_path to the target schema, 
    performs a bulk insert, and commits the transaction.
    """
    if not objects:
        return 0

    try:
        # 1. Set the search path dynamically
        # This forces the insert to happen in the 'target_schema'
        db.execute(text(f"SET search_path TO {schema}"))
        
        # 2. Bulk Save
        # return_defaults=False is faster for large datasets
        db.bulk_save_objects(objects, return_defaults=False)
        
        # 3. Commit
        db.commit()
        return len(objects)
        
    except Exception as e:
        db.rollback()
        raise e
    finally:
        # Safety: Reset to public
        db.execute(text("SET search_path TO public"))


def insert_occupations(db: Session, data: List[Occupation], target_schema: str):
    """Business logic to insert Occupations into a specific schema."""
    # Convert Pydantic schemas to SQLAlchemy Models
    db_objects = [Occupation(**item.dict()) for item in data]
    return _bulk_insert_with_schema(db, db_objects, target_schema)


def insert_skills(db: Session, data: List[Skill], target_schema: str):
    """Business logic to insert Skills into a specific schema."""
    db_objects = [Skill(**item.dict()) for item in data]
    return _bulk_insert_with_schema(db, db_objects, target_schema)


def insert_skill_groups(db: Session, data: List[SkillGroup], target_schema: str):
    """Business logic to insert Skill Groups into a specific schema."""
    db_objects = [SkillGroup(**item.dict()) for item in data]
    return _bulk_insert_with_schema(db, db_objects, target_schema)


def insert_skill_hierarchy(db: Session, data: List[SkillHierarchy], target_schema: str):
    """Business logic to insert Skill Hierarchies into a specific schema."""
    db_objects = [SkillHierarchy(**item.dict()) for item in data]
    return _bulk_insert_with_schema(db, db_objects, target_schema)


def insert_relations(db: Session, data: List[OccupationSkillRelation], target_schema: str):
    """Business logic to insert Occupation-Skill Relations into a specific schema."""
    db_objects = [OccupationSkillRelation(**item.dict()) for item in data]
    return _bulk_insert_with_schema(db, db_objects, target_schema)