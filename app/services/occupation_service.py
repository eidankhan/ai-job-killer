from sqlalchemy.orm import Session
from app.models.occupation import Occupation
from app.schemas.occupation import OccupationSchema

def insert_occupations(db: Session, occupations: list[OccupationSchema]):
    """
    Insert a list of occupations into PostgreSQL.
    Uses bulk insert with upsert (ON CONFLICT DO NOTHING).
    """
    objects = [Occupation(**occ.dict()) for occ in occupations]
    db.bulk_save_objects(objects, return_defaults=False)
    db.commit()
