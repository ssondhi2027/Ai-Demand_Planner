import pandas as pd

REQUIRED_COLUMNS = {"date", "product_name", "demand"}

def validate_csv(df: pd.DataFrame):
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df["date"] = pd.to_datetime(df["date"])
    df["demand"] = df["demand"].astype(float)

    return df.sort_values("date")