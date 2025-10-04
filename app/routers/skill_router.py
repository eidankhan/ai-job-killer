import os
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.utils.skill_cleaner import clean_skill_csv
from app.schemas.skill import SkillSchema
from app.services.skill_service import insert_skills

router = APIRouter(prefix="/skills", tags=["Skills"])

FILE_PATH = "/app/data/skills_en.csv"

@router.post("/load")
def load_skills_from_file(db: Session = Depends(get_db)):
    """
    Load skills from a local CSV file, clean it, and insert into PostgreSQL.
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
        cleaned_df = clean_skill_csv(df)

        # 3. Convert to Pydantic schema objects
        skills = [
            SkillSchema(**row._asdict())
            for row in cleaned_df.itertuples(index=False)
        ]

        # 4. Insert into DB
        insert_skills(db, skills)

        return {
            "status": "success",
            "inserted_records": len(skills),
            "file": FILE_PATH
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error loading file: {str(e)}")
