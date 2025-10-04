import pandas as pd
from app.schemas.occupation_skill_relation import OccupationSkillRelationCreate
from app.schemas.skill import SkillSchema
from app.schemas.skill_hierarchy import SkillHierarchySchema
from app.schemas.skillgroup import SkillGroupSchema
from app.utils.data_cleaner import clean_occupation_csv, clean_skill_csv, clean_skillgroup_csv, clean_skill_hierarchy_csv, clean_occupation_skill_relation_csv
from app.schemas.occupation import OccupationSchema


occupations_csv = "/app/data/occupations_en.csv"
skills_csv = "/app/data/skills_en.csv"
skill_groups_csv = "/app/data/SkillGroups_en.csv"
skill_hierarchy_csv = "/app/data/SkillHierarchy_en.csv"
occupation_skills_relation_csv = "/app/data/OccupationSkillsRelation_en.csv"


def clean():
    # 1. Read CSV into DataFrame
    occupations_df = pd.read_csv(occupations_csv, dtype=str, keep_default_na=False)
    skills_df = pd.read_csv(skills_csv, dtype=str, keep_default_na=False)
    skill_groups_df = pd.read_csv(skill_groups_csv, dtype=str, keep_default_na=False)
    skill_hierarchy_df = pd.read_csv(skill_hierarchy_csv, dtype=str, keep_default_na=False)
    occupation_skills_selation_en_df = pd.read_csv(occupation_skills_relation_csv, dtype=str, keep_default_na=False)
    
    # 2. Clean DataFrame
    occupations_cleaned_df = clean_occupation_csv(occupations_df)
    skills_cleaned_df = clean_occupation_csv(skills_df)
    skill_groups_cleaned_df = clean_occupation_csv(skill_groups_df)
    skill_hierarchy_cleaned_df = clean_occupation_csv(skill_hierarchy_df)
    occupation_skills_relation_cleaned_df = clean_occupation_csv(occupation_skills_selation_en_df)

    # 3. Convert rows to Pydantic schema objects
    occupations = [
        OccupationSchema(**row._asdict())
        for row in occupations_cleaned_df.itertuples(index=False)
    ]

    skills = [
        SkillSchema(**row._asdict())
        for row in skills_cleaned_df.itertuples(index=False)
    ]

    skill_groups = [
                SkillGroupSchema(**row._asdict())
                for row in skill_groups_cleaned_df.itertuples(index=False)
            ]
    
    skill_hierarchies = [
            SkillHierarchySchema(**row._asdict()) for row in skill_hierarchy_cleaned_df.itertuples(index=False)
        ]
    
    relations = [
        OccupationSkillRelationCreate(
            occupationUri=row["occupationUri"],
            relationType=row.get("relationType"),
            skillType=row.get("skillType"),
            skillUri=row["skillUri"]
        )
        for row in occupation_skills_relation_cleaned_df.to_dict(orient="records")
    ]

    return {
        "occupations": occupations,
        "skills":skills,
        "skill_groups":skill_groups,
        "skill_hierarchies":skill_hierarchies,
        "relations":relations
    }