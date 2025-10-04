from app.services.occupation_skill_relation_service import insert_occupation_skill_relations
from app.services.skill_hierarchy_service import insert_skill_hierarchies
from app.services.skill_service import insert_skills
from app.services.skillgroup_service import insert_skillgroups
from sqlalchemy.orm import Session
from app.services.data_cleaner import clean
from app.services.occupation_service import insert_occupations

def import_data(db: Session):
    occupations,skills,skill_groups,skill_hierarchies,relations = clean()
    print("Data cleaned successfully")

    try:
        # 4. Insert into DB
        insert_occupations(db, occupations)
        insert_skills(db, skills)
        insert_skillgroups(db, skill_groups)
        insert_skill_hierarchies(db, skill_hierarchies)
        insert_occupation_skill_relations(db, relations)

        print("Data has been imported successfully")
    except Exception:
        print("Error occured while importing the data")
