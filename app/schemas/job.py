# app/schemas/job.py
from pydantic import BaseModel
from typing import Optional

class ProfessionOut(BaseModel):
    id: int
    title: str
    score: Optional[float] = None  # ✅ allow fractional scores
    description: Optional[str] = None

    class Config:
        orm_mode = True


class SkillOut(BaseModel):
    id: int
    name: str
    risk_level: str

    class Config:
        orm_mode = True
