from sqlalchemy.orm import Session
from app.models.occupation_skill_relation import OccupationSkillRelation
from app.models.occupation import Occupation
from app.models.skill import Skill
from app.schemas.occupation_skill_relation import OccupationSkillRelationCreate

def insert_occupation_skill_relations(db: Session, relations: list[OccupationSkillRelationCreate]) -> int:
    inserted = 0

    # 1. Get all occupations and skills into dicts
    occupation_map = {
        o.conceptUri: o.id for o in db.query(Occupation).all()
    }
    skill_map = {
        s.conceptUri: s.id for s in db.query(Skill).all()
    }

    # 2. Existing relations (to avoid duplicates)
    existing_relations = set(
        (r.occupation_id, r.skill_id)
        for r in db.query(OccupationSkillRelation).all()
    )

    # 3. Prepare objects to add
    to_add = []
    for rel in relations:
        occ_id = occupation_map.get(rel.occupationUri)
        skill_id = skill_map.get(rel.skillUri)
        if not occ_id or not skill_id:
            continue

        if (occ_id, skill_id) in existing_relations:
            continue

        to_add.append(
            OccupationSkillRelation(
                occupation_id=occ_id,
                skill_id=skill_id,
                relationType=rel.relationType,
                skillType=rel.skillType
            )
        )
        existing_relations.add((occ_id, skill_id))
        inserted += 1

    # 4. Bulk insert
    if to_add:
        db.bulk_save_objects(to_add)
        db.commit()

    return inserted
