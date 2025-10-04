import pandas as pd
import numpy as np

def clean_occupation_csv(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans a DataFrame: handles missing columns, trims strings,
    drops duplicates/nulls, and ensures all expected columns exist.
    """
    # Strip whitespace from column names
    df.columns = df.columns.str.strip()

    expected_cols = [
        "conceptType","conceptUri","iscoGroup","preferredLabel","altLabels",
        "hiddenLabels","status","modifiedDate","regulatedProfessionNote",
        "scopeNote","definition","inScheme","description","code"
    ]

    # Ensure all expected columns exist
    for col in expected_cols:
        if col not in df.columns:
            df[col] = None

    # Drop completely empty rows
    df.dropna(how="all", inplace=True)

    # Strip whitespace from all string cells
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    # Drop duplicates by conceptUri
    df.drop_duplicates(subset=["conceptUri"], inplace=True)

    return df[expected_cols]


def clean_skill_csv(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans Skills DataFrame: ensures expected columns, trims text, drops duplicates/nulls.
    """
    df.columns = df.columns.str.strip()

    expected_cols = [
        "conceptType","conceptUri","skillType","reuseLevel","preferredLabel",
        "altLabels","hiddenLabels","status","modifiedDate","scopeNote",
        "definition","inScheme","description"
    ]

    # Ensure all expected columns exist
    for col in expected_cols:
        if col not in df.columns:
            df[col] = None

    # Drop empty rows
    df.dropna(how="all", inplace=True)

    # Trim whitespace
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    # Drop duplicates by conceptUri
    df.drop_duplicates(subset=["conceptUri"], inplace=True)

    return df[expected_cols]


def clean_skillgroup_csv(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans SkillGroups DataFrame: ensures expected columns, trims text, drops duplicates/nulls.
    """
    df.columns = df.columns.str.strip()

    expected_cols = [
        "conceptType","conceptUri","preferredLabel","altLabels","hiddenLabels",
        "status","modifiedDate","scopeNote","inScheme","description","code"
    ]

    # Ensure all expected columns exist
    for col in expected_cols:
        if col not in df.columns:
            df[col] = None

    # Drop completely empty rows
    df.dropna(how="all", inplace=True)

    # Trim whitespace from all string values
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    # Normalize empty strings to None
    df.replace({"": None, " ": None, np.nan: None}, inplace=True)

    # Fix modifiedDate specifically (force empty → None, else keep string)
    if "modifiedDate" in df.columns:
        df["modifiedDate"] = df["modifiedDate"].apply(lambda x: None if not x else x)

    # Drop duplicates based on conceptUri
    df.drop_duplicates(subset=["conceptUri"], inplace=True)

    return df[expected_cols]

def clean_skill_hierarchy_csv(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans SkillHierarchy DataFrame: ensures expected columns, trims, handles nulls, drops duplicates.
    """
    df.columns = df.columns.str.strip()

    expected_cols = [
        "Level 0 URI","Level 0 preferred term",
        "Level 1 URI","Level 1 preferred term",
        "Level 2 URI","Level 2 preferred term",
        "Level 3 URI","Level 3 preferred term",
        "Description","Scope note",
        "Level 0 code","Level 1 code","Level 2 code","Level 3 code"
    ]

    # Ensure all expected columns exist
    for col in expected_cols:
        if col not in df.columns:
            df[col] = None

    # Drop completely empty rows
    df.dropna(how="all", inplace=True)

    # Trim whitespace
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    # Normalize empty → None
    df.replace({"": None, " ": None, np.nan: None}, inplace=True)

    # Drop duplicates (all columns)
    df.drop_duplicates(inplace=True)

    # Rename columns to snake_case
    return df[expected_cols].rename(columns={
        "Level 0 URI": "level_0_uri",
        "Level 0 preferred term": "level_0_preferred_term",
        "Level 1 URI": "level_1_uri",
        "Level 1 preferred term": "level_1_preferred_term",
        "Level 2 URI": "level_2_uri",
        "Level 2 preferred term": "level_2_preferred_term",
        "Level 3 URI": "level_3_uri",
        "Level 3 preferred term": "level_3_preferred_term",
        "Description": "description",
        "Scope note": "scope_note",
        "Level 0 code": "level_0_code",
        "Level 1 code": "level_1_code",
        "Level 2 code": "level_2_code",
        "Level 3 code": "level_3_code",
    })

def clean_occupation_skill_relation_csv(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean Occupation-Skill Relations CSV:
    - Ensure expected columns exist
    - Strip whitespace from column names and values
    - Drop rows missing critical fields (occupationUri, skillUri)
    - Deduplicate rows
    """
    # Normalize column names
    df.columns = [col.strip() for col in df.columns]

    expected_cols = ["occupationUri", "relationType", "skillType", "skillUri"]
    missing = [c for c in expected_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing expected columns: {missing}")

    # Keep only required columns
    df = df[expected_cols]

    # Strip whitespace in string values
    for col in df.columns:
        df[col] = df[col].astype(str).str.strip()

    # Drop rows missing occupationUri or skillUri
    df = df[df["occupationUri"].notna() & (df["occupationUri"] != "")]
    df = df[df["skillUri"].notna() & (df["skillUri"] != "")]

    # Drop duplicates
    df = df.drop_duplicates(
        subset=["occupationUri", "skillUri", "relationType", "skillType"]
    )

    return df
