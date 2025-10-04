from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SkillSchema(BaseModel):
    conceptType: Optional[str]
    conceptUri: str
    skillType: Optional[str]
    reuseLevel: Optional[str]
    preferredLabel: Optional[str]
    altLabels: Optional[str]
    hiddenLabels: Optional[str]
    status: Optional[str]
    modifiedDate: Optional[datetime]
    scopeNote: Optional[str]
    definition: Optional[str]
    inScheme: Optional[str]
    description: Optional[str]

    class Config:
        orm_mode = True
