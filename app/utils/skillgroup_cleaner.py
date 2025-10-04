import pandas as pd
import numpy as np

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
