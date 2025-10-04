from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class OccupationSchema(BaseModel):
    conceptType: Optional[str]
    conceptUri: str
    iscoGroup: Optional[str]
    preferredLabel: Optional[str]
    altLabels: Optional[str]
    hiddenLabels: Optional[str]
    status: Optional[str]
    modifiedDate: Optional[datetime]
    regulatedProfessionNote: Optional[str]
    scopeNote: Optional[str]
    definition: Optional[str]
    inScheme: Optional[str]
    description: Optional[str]
    code: Optional[str]

    class Config:
        orm_mode = True
