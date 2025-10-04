import os
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.occupation_skill_relation import OccupationSkillRelationCreate
from app.services.occupation_skill_relation_service import insert_occupation_skill_relations
from app.utils.occupation_skill_relation_cleaner import clean_occupation_skill_relation_csv

router = APIRouter(prefix="/occupation-skill-relations", tags=["Occupation-Skill Relations"])

FILE_PATH = "/app/data/OccupationSkillsRelation_en.csv"


@router.post("/load")
def load_occupation_skill_relations_from_file(db: Session = Depends(get_db)):
    """
    Load occupation-skill relations from a local CSV file, clean it, and insert into PostgreSQL.
    """
    if not os.path.exists(FILE_PATH):
        raise HTTPException(
            status_code=404,
            detail=f"CSV file not found at path: {FILE_PATH}"
        )

    try:
        # 1. Read CSV
        df = pd.read_csv(FILE_PATH, dtype=str, keep_default_na=False)

        # 2. Clean CSV
        cleaned_df = clean_occupation_skill_relation_csv(df)

        # 3. Convert to Pydantic schema objects
        relations = [
            OccupationSkillRelationCreate(
                occupationUri=row["occupationUri"],
                relationType=row.get("relationType"),
                skillType=row.get("skillType"),
                skillUri=row["skillUri"]
            )
            for row in cleaned_df.to_dict(orient="records")
        ]

        # 4. Insert into DB
        inserted_count = insert_occupation_skill_relations(db, relations)

        return {
            "status": "success",
            "inserted_records": inserted_count,
            "file": FILE_PATH
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error loading file: {str(e)}")
