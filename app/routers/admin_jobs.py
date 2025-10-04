# from fastapi import APIRouter, Depends, Query
# from sqlalchemy.orm import Session
# from app.core.database import get_db
# from app.services.esco_ingestion import (
#     ingest_occupations,
#     ingest_skills,
#     ingest_occupation_skills,
#     ingest_skill_groups,
#     ingest_skill_hierarchy
# )

# router = APIRouter(prefix="/admin", tags=["admin"])

# @router.post("/ingest-esco")
# def ingest_esco_data(force: bool = Query(False), db: Session = Depends(get_db)):
#     """
#     Ingest ESCO CSV data into the database.
#     Set `force=true` to clear existing data before reloading.
#     """
#     ingest_occupations(db, force)
#     ingest_skills(db, force)
#     ingest_occupation_skills(db, force)
#     ingest_skill_groups(db, force)
#     ingest_skill_hierarchy(db, force)
#     return {"status": "success", "message": "ESCO data ingested successfully"}
