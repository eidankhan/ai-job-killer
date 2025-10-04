import pandas as pd

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
