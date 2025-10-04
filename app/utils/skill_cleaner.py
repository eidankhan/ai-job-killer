import pandas as pd

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
