import pandas as pd

def clean_occupations(df: pd.DataFrame) -> pd.DataFrame:
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
