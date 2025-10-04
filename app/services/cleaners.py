# import pandas as pd
# from app.utils.text_utils import normalize_labels, parse_date

# def clean_occupations(df: pd.DataFrame, report: dict) -> pd.DataFrame:
#     df.drop_duplicates(inplace=True)
#     df.fillna("", inplace=True)
#     df["preferredLabel"] = df["preferredLabel"].str.strip()
#     df["altLabels"] = df["altLabels"].apply(normalize_labels)
#     df["hiddenLabels"] = df["hiddenLabels"].apply(normalize_labels)
#     df["modifiedDate"] = df["modifiedDate"].apply(parse_date)
#     return df

# def clean_skills(df: pd.DataFrame, report: dict) -> pd.DataFrame:
#     df.drop_duplicates(inplace=True)
#     df.fillna("", inplace=True)
#     df["preferredLabel"] = df["preferredLabel"].str.strip()
#     df["altLabels"] = df["altLabels"].apply(normalize_labels)
#     df["hiddenLabels"] = df["hiddenLabels"].apply(normalize_labels)
#     df["modifiedDate"] = df["modifiedDate"].apply(parse_date)
#     return df

# def clean_occupation_skills_relation(df: pd.DataFrame, report: dict) -> pd.DataFrame:
#     df.drop_duplicates(inplace=True)
#     df.fillna("", inplace=True)
#     return df

# def clean_skill_groups(df: pd.DataFrame, report: dict) -> pd.DataFrame:
#     df.drop_duplicates(inplace=True)
#     df.fillna("", inplace=True)
#     df["preferredLabel"] = df["preferredLabel"].str.strip()
#     df["altLabels"] = df["altLabels"].apply(normalize_labels)
#     df["hiddenLabels"] = df["hiddenLabels"].apply(normalize_labels)
#     df["modifiedDate"] = df["modifiedDate"].apply(parse_date)
#     return df

# def clean_skill_hierarchy(df: pd.DataFrame, report: dict) -> pd.DataFrame:
#     df.drop_duplicates(inplace=True)
#     df.fillna("", inplace=True)
#     return df

# CLEANER_MAP = {
#     "occupations": clean_occupations,
#     "skills": clean_skills,
#     "occupation_skills_relation": clean_occupation_skills_relation,
#     "skill_groups": clean_skill_groups,
#     "skill_hierarchy": clean_skill_hierarchy,
# }
