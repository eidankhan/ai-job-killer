import os
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.utils.skillgroup_cleaner import clean_skillgroup_csv
from app.schemas.skillgroup import SkillGroupSchema
from app.services.skillgroup_service import insert_skillgroups

router = APIRouter(prefix="/skillgroups", tags=["Skill Groups"])

FILE_PATH = "/app/data/SkillGroups_en.csv"

@router.post("/load")
def load_skillgroups_from_file(db: Session = Depends(get_db)):
    """
    Load skill groups from a local CSV file, clean it, and insert into PostgreSQL.
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
        cleaned_df = clean_skillgroup_csv(df)

        # 3. Convert rows to Pydantic schema objects
        skillgroups = [
            SkillGroupSchema(**row._asdict())
            for row in cleaned_df.itertuples(index=False)
        ]

        # 4. Insert into DB
        insert_skillgroups(db, skillgroups)

        return {
            "status": "success",
            "inserted_records": len(skillgroups),
            "file": FILE_PATH
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error loading file: {str(e)}")
