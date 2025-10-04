from pydantic import BaseModel
from typing import Optional

class SkillHierarchySchema(BaseModel):
    level_0_uri: Optional[str]
    level_0_preferred_term: Optional[str]
    level_1_uri: Optional[str]
    level_1_preferred_term: Optional[str]
    level_2_uri: Optional[str]
    level_2_preferred_term: Optional[str]
    level_3_uri: Optional[str]
    level_3_preferred_term: Optional[str]
    description: Optional[str]
    scope_note: Optional[str]
    level_0_code: Optional[str]
    level_1_code: Optional[str]
    level_2_code: Optional[str]
    level_3_code: Optional[str]

    class Config:
        orm_mode = True
