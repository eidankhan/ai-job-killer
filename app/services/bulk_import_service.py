import os
import pandas as pd
from sqlalchemy.orm import Session

from app.utils.data_cleaner import clean_occupation_csv
from app.schemas.occupation import OccupationSchema
from app.services.occupation_service import insert_occupations

from app.utils.skill_cleaner import clean_skill_csv
from app.schemas.skill import SkillSchema
from app.services.skill_service import insert_skills

from app.utils.data_cleaner import clean_skillgroup_csv
from app.schemas.skillgroup import SkillGroupSchema
from app.services.skillgroup_service import insert_skillgroups

from app.utils.skill_hierarchy_cleaner import clean_skill_hierarchy_csv
from app.schemas.skill_hierarchy import SkillHierarchySchema
from app.services.skill_hierarchy_service import insert_skill_hierarchies

from app.utils.occupation_skill_relation_cleaner import clean_occupation_skill_relation_csv
from app.schemas.occupation_skill_relation import OccupationSkillRelationCreate
from app.services.occupation_skill_relation_service import insert_occupation_skill_relations


class BulkImportService:

    FILES = {
        "occupations": "/app/data/occupations_en.csv",
        "skills": "/app/data/skills_en.csv",
        "skill_groups": "/app/data/SkillGroups_en.csv",
        "skill_hierarchy": "/app/data/SkillHierarchy_en.csv",
        "occupation_skill_relations": "/app/data/OccupationSkillsRelation_en.csv"
    }

    @staticmethod
    def import_all(db: Session) -> dict:
        results = {}

        # ---------------- Occupations ----------------
        df = pd.read_csv(BulkImportService.FILES["occupations"], dtype=str, keep_default_na=False)
        cleaned_df = clean_occupation_csv(df)
        occupations = [OccupationSchema(**row) for row in cleaned_df.to_dict(orient="records")]
        inserted_occ = insert_occupations(db, occupations)
        results["occupations"] = inserted_occ

        # ---------------- Skills ----------------
        df = pd.read_csv(BulkImportService.FILES["skills"], dtype=str, keep_default_na=False)
        cleaned_df = clean_skill_csv(df)
        skills = [SkillSchema(**row) for row in cleaned_df.to_dict(orient="records")]
        inserted_skills = insert_skills(db, skills)
        results["skills"] = inserted_skills

        # ---------------- Skill Groups ----------------
        df = pd.read_csv(BulkImportService.FILES["skill_groups"], dtype=str, keep_default_na=False)
        cleaned_df = clean_skillgroup_csv(df)
        skill_groups = [SkillGroupSchema(**row) for row in cleaned_df.to_dict(orient="records")]
        inserted_groups = insert_skillgroups(db, skill_groups)
        results["skill_groups"] = inserted_groups

        # ---------------- Skill Hierarchy ----------------
        df = pd.read_csv(BulkImportService.FILES["skill_hierarchy"], dtype=str, keep_default_na=False)
        cleaned_df = clean_skill_hierarchy_csv(df)
        hierarchies = [SkillHierarchySchema(**row) for row in cleaned_df.to_dict(orient="records")]
        inserted_hierarchy = insert_skill_hierarchies(db, hierarchies)
        results["skill_hierarchy"] = inserted_hierarchy

        # ---------------- Occupation-Skill Relations ----------------
        df = pd.read_csv(BulkImportService.FILES["occupation_skill_relations"], dtype=str, keep_default_na=False)
        cleaned_df = clean_occupation_skill_relation_csv(df)
        relations = [
            OccupationSkillRelationCreate(
                occupationUri=row["occupationUri"],
                relationType=row.get("relationType"),
                skillType=row.get("skillType"),
                skillUri=row["skillUri"]
            )
            for row in cleaned_df.to_dict(orient="records")
        ]
        inserted_relations = insert_occupation_skill_relations(db, relations)
        results["occupation_skill_relations"] = inserted_relations

        return results
