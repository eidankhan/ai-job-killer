import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.utils.skill_hierarchy_cleaner import clean_skill_hierarchy_csv
from app.schemas.skill_hierarchy import SkillHierarchySchema
from app.services.skill_hierarchy_service import insert_skill_hierarchies

router = APIRouter(prefix="/skill-hierarchy", tags=["SkillHierarchy"])

@router.post("/load")
def load_skill_hierarchy_from_file(db: Session = Depends(get_db)):
    """
    Load skill hierarchy from a local CSV file, clean it, and insert into PostgreSQL.
    """
    file_path = "/app/data/SkillHierarchy_en.csv"

    try:
        # Read CSV
        df = pd.read_csv(file_path, dtype=str, keep_default_na=False)

        # Clean CSV
        cleaned_df = clean_skill_hierarchy_csv(df)

        # Convert rows to Pydantic schema objects
        skill_hierarchies = [
            SkillHierarchySchema(**row._asdict()) for row in cleaned_df.itertuples(index=False)
        ]

        # Insert into DB
        insert_skill_hierarchies(db, skill_hierarchies)

        return {"status": "success", "inserted_records": len(skill_hierarchies)}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error loading file: {str(e)}")
