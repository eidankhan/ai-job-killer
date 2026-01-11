"""
API Router for loading CSV data into specific database schemas.
"""
import os
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
# Import the Service Layer we just created
import app.services.data_loader_service as service

# Import Schemas

from app.models.occupation import Occupation
from app.models.skill import Skill
from app.models.skill_group import SkillGroup
from app.models.skill_hierarchy import SkillHierarchy
from app.models.occupation_skill_relation import OccupationSkillRelation


# Import Cleaning Utils (Assuming these exist or you will create them similar to occupations)
from app.utils.occupations_cleaner import clean_occupations
from app.utils.skill_cleaner import clean_skill_csv
from app.utils.skill_hierarchy_cleaner import clean_skill_hierarchy_csv
from app.utils.occupation_skill_relation_cleaner import clean_occupation_skill_relation_csv
from app.utils.skillgroup_cleaner import clean_skillgroup_csv

router = APIRouter(tags=["Data Loaders"])

# CSV File Paths (Inside Docker Container)
PATHS = {
    "occupation": "/app/data/occupations_en.csv",
    "skill": "/app/data/skills_en.csv",
    "skill_group": "/app/data/skillGroups_en.csv",
    "hierarchy": "/app/data/broaderRelationsSkillPillar.csv",
    "relations": "/app/data/occupationSkillRelations.csv"
}

def _load_csv_dataframe(file_path: str) -> pd.DataFrame:
    """Helper to read CSV safely."""
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
    return pd.read_csv(file_path, dtype=str, keep_default_na=False)


@router.post("/occupations/load", summary="Load Occupations CSV")
def load_occupations(
    target_schema: str = Query(..., description="Schema to insert data into"),
    db: Session = Depends(get_db)
):
    try:
        df = _load_csv_dataframe(PATHS["occupation"])
        cleaned_df = clean_occupations(df)
        
        # Convert to Pydantic
        data_list = [Occupation(**row._asdict()) for row in cleaned_df.itertuples(index=False)]
        
        # Call Service
        count = service.insert_occupations(db, data_list, target_schema)
        
        return {"status": "success", "schema": target_schema, "inserted": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/skills/load", summary="Load Skills CSV")
def load_skills(
    target_schema: str = Query(..., description="Schema to insert data into"),
    db: Session = Depends(get_db)
):
    try:
        df = _load_csv_dataframe(PATHS["skill"])
        # Assuming you have a clean_skills function
        cleaned_df = clean_skill_csv(df) 
        
        data_list = [Skill(**row._asdict()) for row in cleaned_df.itertuples(index=False)]
        count = service.insert_skills(db, data_list, target_schema)
        
        return {"status": "success", "schema": target_schema, "inserted": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/skillgroups/load", summary="Load Skill Groups CSV")
def load_skill_groups(
    target_schema: str = Query(..., description="Schema to insert data into"),
    db: Session = Depends(get_db)
):
    try:
        df = _load_csv_dataframe(PATHS["skill_group"])
        cleaned_df = clean_skillgroup_csv(df)
        
        data_list = [SkillGroup(**row._asdict()) for row in cleaned_df.itertuples(index=False)]
        count = service.insert_skill_groups(db, data_list, target_schema)
        
        return {"status": "success", "schema": target_schema, "inserted": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/skill-hierarchy/load", summary="Load Skill Hierarchy CSV")
def load_skill_hierarchy(
    target_schema: str = Query(..., description="Schema to insert data into"),
    db: Session = Depends(get_db)
):
    try:
        df = _load_csv_dataframe(PATHS["hierarchy"])
        cleaned_df = clean_skill_hierarchy_csv(df)
        
        data_list = [SkillHierarchy(**row._asdict()) for row in cleaned_df.itertuples(index=False)]
        count = service.insert_skill_hierarchy(db, data_list, target_schema)
        
        return {"status": "success", "schema": target_schema, "inserted": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/occupation-skill-relations/load", summary="Load Relations CSV")
def load_relations(
    target_schema: str = Query(..., description="Schema to insert data into"),
    db: Session = Depends(get_db)
):
    try:
        df = _load_csv_dataframe(PATHS["relations"])
        cleaned_df = clean_occupation_skill_relation_csv(df)
        
        data_list = [OccupationSkillRelation(**row._asdict()) for row in cleaned_df.itertuples(index=False)]
        count = service.insert_relations(db, data_list, target_schema)
        
        return {"status": "success", "schema": target_schema, "inserted": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bulk-import/load-all", summary="Bulk Load All (Sequence)")
def load_all_tables(
    target_schema: str = Query(..., description="Schema to insert data into"),
    db: Session = Depends(get_db)
):
    """
    Orchestrator: Runs all loaders in the correct order (Dependencies first!).
    """
    try:
        results = {}
        
        # 1. Independent Tables
        results['occupations'] = load_occupations(target_schema, db)
        results['skills'] = load_skills(target_schema, db)
        results['skill_groups'] = load_skill_groups(target_schema, db)
        results['hierarchy'] = load_skill_hierarchy(target_schema, db)
        
        # 2. Dependent Tables (Foreign Keys)
        # Relations depend on both Occupation and Skill being loaded first
        results['relations'] = load_relations(target_schema, db)
        
        return {"status": "success", "report": results}
        
    except Exception as e:
        # Note: Since individual functions commit their own transactions, 
        # a failure here might leave partial data in the staging schema.
        # But that's okay, because 'staging' isn't live yet!
        raise HTTPException(status_code=500, detail=f"Bulk load failed: {str(e)}")