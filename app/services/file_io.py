import pandas as pd

def read_csv_file(path: str) -> pd.DataFrame:
    """Read CSV as string dtype, keep empty as empty strings."""
    return pd.read_csv(path, dtype=str, keep_default_na=False)

def save_cleaned_csv(df: pd.DataFrame, path: str):
    """Save cleaned CSV to disk."""
    df.to_csv(path, index=False, encoding="utf-8")
