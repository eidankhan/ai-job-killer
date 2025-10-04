from pydantic import BaseModel

class OccupationSkillRelationBase(BaseModel):
    occupationUri: str
    relationType: str | None = None
    skillType: str | None = None
    skillUri: str

class OccupationSkillRelationCreate(OccupationSkillRelationBase):
    pass

class OccupationSkillRelationSchema(OccupationSkillRelationBase):
    id: int

    class Config:
        from_attributes = True
