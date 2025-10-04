import os
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.utils.occupations_cleaner import clean_occupations
from app.schemas.occupation import OccupationSchema
from app.services.occupation_service import insert_occupations

router = APIRouter(prefix="/occupations", tags=["Occupations"])

# Path to your local CSV
FILE_PATH = "/app/data/occupations_en.csv"


@router.post("/load")
def load_occupations_from_file(db: Session = Depends(get_db)):
    """
    Load occupations from a local CSV file, clean it, and insert into PostgreSQL.
    """
    if not os.path.exists(FILE_PATH):
        raise HTTPException(
            status_code=404,
            detail=f"CSV file not found at path: {FILE_PATH}"
        )

    try:
        # 1. Read CSV into DataFrame
        df = pd.read_csv(FILE_PATH, dtype=str, keep_default_na=False)

        # 2. Clean DataFrame
        cleaned_df = clean_occupations(df)

        # 3. Convert rows to Pydantic schema objects
        occupations = [
            OccupationSchema(**row._asdict())
            for row in cleaned_df.itertuples(index=False)
        ]

        # 4. Insert into DB
        insert_occupations(db, occupations)

        return {
            "status": "success",
            "inserted_records": len(occupations),
            "file": FILE_PATH
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error loading file: {str(e)}"
        )
