from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SkillGroupSchema(BaseModel):
    conceptType: Optional[str]
    conceptUri: str
    preferredLabel: Optional[str]
    altLabels: Optional[str]
    hiddenLabels: Optional[str]
    status: Optional[str]
    modifiedDate: Optional[datetime]
    scopeNote: Optional[str]
    inScheme: Optional[str]
    description: Optional[str]
    code: Optional[str]

    class Config:
        orm_mode = True
