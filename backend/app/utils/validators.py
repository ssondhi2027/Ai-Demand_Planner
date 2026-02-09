import pandas as pd

REQUIRED_COLUMNS = {"date", "product_name", "demand"}

def validate_csv(df: pd.DataFrame) -> pd.DataFrame:
    return validate_dataset(df, REQUIRED_COLUMNS)

def validate_dataset(df: pd.DataFrame, required_columns: set) -> pd.DataFrame:
    if df is None or df.empty:
        raise ValueError("Dataset is empty")

    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df = df.copy()
    df["date"] = pd.to_datetime(df["date"],format="%Y-%m-%d", errors="coerce")
    if df["date"].isna().any():
        raise ValueError("Invalid or missing dates in 'date' column")

    df["demand"] = pd.to_numeric(df["demand"], errors="coerce")
    if df["demand"].isna().any():
        raise ValueError("Invalid or missing values in 'demand' column")

    if (df["demand"] < 0).any():
        raise ValueError("Demand values must be non-negative")

    return df.sort_values("date")
