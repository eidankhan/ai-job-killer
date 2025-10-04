# # app/routes/jobs.py
# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from app.core.database import get_db
# from app.services.job_service import search_professions
# from app.schemas.job import ProfessionOut
# from typing import List
# from app.models.skill import Skill
# from app.schemas.job import SkillOut


# router = APIRouter(prefix="/jobs", tags=["jobs"])

# @router.get("/search", response_model=List[ProfessionOut])
# def search_jobs(q: str, db: Session = Depends(get_db)):
#     if not q:
#         raise HTTPException(status_code=400, detail="Query parameter 'q' is required")
#     return search_professions(db, q)


# from app.schemas.job import SkillOut

# @router.get("/{profession_id}/skills", response_model=List[SkillOut])
# def profession_skills(profession_id: int, db: Session = Depends(get_db)):
#     skills = db.query(Skill).filter_by(profession_id=profession_id).all()
#     if not skills:
#         raise HTTPException(status_code=404, detail="Profession not found or no skills loaded")
#     return skills
