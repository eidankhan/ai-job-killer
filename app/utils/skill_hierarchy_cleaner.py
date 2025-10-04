import pandas as pd
import numpy as np

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
