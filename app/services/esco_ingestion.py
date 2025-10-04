# import pandas as pd
# from sqlalchemy.orm import Session
# from app.models.occupation import Occupation
# from app.models.skill import Skill
# from app.models.occupation_skill import OccupationSkill
# from app.models.skill_group import SkillGroup
# from app.models.skill_hierarchy import SkillHierarchy
# import os

# DATA_DIR = "/app/data"

# # # # Paths relative to project root
# # DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "ESCO-dataset-v1.1.1")

# def ingest_occupations(db: Session, force: bool = False):
#     path = f"{DATA_DIR}/occupations_en.csv"
#     df = pd.read_csv(path)

#     if force:
#         db.query(Occupation).delete()

#     for _, row in df.iterrows():
#         occ = Occupation(
#             concept_uri=row["conceptUri"],
#             isco_group=row.get("iscoGroup"),
#             preferred_label=row.get("preferredLabel"),
#             alt_labels=row.get("altLabels"),
#             hidden_labels=row.get("hiddenLabels"),
#             status=row.get("status"),
#             modified_date=row.get("modifiedDate"),
#             regulated_note=row.get("regulatedProfessionNote"),
#             scope_note=row.get("scopeNote"),
#             definition=row.get("definition"),
#             in_scheme=row.get("inScheme"),
#             description=row.get("description"),
#             code=row.get("code")
#         )
#         db.add(occ)
#     db.commit()


# def ingest_skills(db: Session, force: bool = False):
#     path = f"{DATA_DIR}/skills_en.csv"
#     df = pd.read_csv(path)

#     if force:
#         db.query(Skill).delete()

#     for _, row in df.iterrows():
#         skill = Skill(
#             concept_uri=row["conceptUri"],
#             skill_type=row.get("skillType"),
#             reuse_level=row.get("reuseLevel"),
#             preferred_label=row.get("preferredLabel"),
#             alt_labels=row.get("altLabels"),
#             hidden_labels=row.get("hiddenLabels"),
#             status=row.get("status"),
#             modified_date=row.get("modifiedDate"),
#             scope_note=row.get("scopeNote"),
#             definition=row.get("definition"),
#             in_scheme=row.get("inScheme"),
#             description=row.get("description")
#         )
#         db.add(skill)
#     db.commit()


# def ingest_occupation_skills(db: Session, force: bool = False):
#     path = f"{DATA_DIR}/occupation_skill_relations_en.csv"
#     df = pd.read_csv(path)

#     if force:
#         db.query(OccupationSkill).delete()

#     for _, row in df.iterrows():
#         rel = OccupationSkill(
#             occupation_uri=row["occupationUri"],
#             relation_type=row.get("relationType"),
#             skill_type=row.get("skillType"),
#             skill_uri=row["skillUri"]
#         )
#         db.add(rel)
#     db.commit()


# def ingest_skill_groups(db: Session, force: bool = False):
#     path = f"{DATA_DIR}/skill_groups_en.csv"
#     df = pd.read_csv(path)

#     if force:
#         db.query(SkillGroup).delete()

#     for _, row in df.iterrows():
#         group = SkillGroup(
#             concept_uri=row["conceptUri"],
#             preferred_label=row.get("preferredLabel"),
#             alt_labels=row.get("altLabels"),
#             hidden_labels=row.get("hiddenLabels"),
#             status=row.get("status"),
#             modified_date=row.get("modifiedDate"),
#             scope_note=row.get("scopeNote"),
#             in_scheme=row.get("inScheme"),
#             description=row.get("description"),
#             code=row.get("code")
#         )
#         db.add(group)
#     db.commit()


# def ingest_skill_hierarchy(db: Session, force: bool = False):
#     path = f"{DATA_DIR}/skill_hierarchy_en.csv"
#     df = pd.read_csv(path)

#     if force:
#         db.query(SkillHierarchy).delete()

#     for _, row in df.iterrows():
#         hierarchy = SkillHierarchy(
#             level_0_uri=row["Level 0 URI"],
#             level_0_label=row["Level 0 preferred term"],
#             level_1_uri=row["Level 1 URI"],
#             level_1_label=row["Level 1 preferred term"],
#             level_2_uri=row["Level 2 URI"],
#             level_2_label=row["Level 2 preferred term"],
#             level_3_uri=row["Level 3 URI"],
#             level_3_label=row["Level 3 preferred term"],
#             description=row.get("Description"),
#             scope_note=row.get("Scope note"),
#             level_0_code=row.get("Level 0 code"),
#             level_1_code=row.get("Level 1 code"),
#             level_2_code=row.get("Level 2 code"),
#             level_3_code=row.get("Level 3 code")
#         )
#         db.add(hierarchy)
#     db.commit()
