import uuid
import pandas as pd
from app.config import RAW_DATA_DIR
from app.utils.validators import validate_csv

def save_uploaded_csv(file) -> str:
    dataset_id = str(uuid.uuid4())
    path = RAW_DATA_DIR / f"{dataset_id}.csv"

    df = pd.read_csv(file)
    df = validate_csv(df)
    df.to_csv(path, index=False)

    return dataset_id, len(df)

def load_dataset(dataset_id: str) -> pd.DataFrame:
    path = RAW_DATA_DIR / f"{dataset_id}.csv"
    return pd.read_csv(path, parse_dates=["date"])