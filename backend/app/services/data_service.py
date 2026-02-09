import logging
import uuid
from dataclasses import dataclass
from typing import BinaryIO

import pandas as pd
from fastapi import UploadFile

from app.config import MAX_ROWS, MAX_UPLOAD_MB, RAW_DATA_DIR
from app.utils.validators import REQUIRED_COLUMNS, validate_dataset

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class UploadResult:
    dataset_id: str
    rows: int

def _get_file_size_mb(file: BinaryIO) -> float:
    pos = file.tell()
    file.seek(0, 2)
    size = file.tell()
    file.seek(pos)
    return size / (1024 * 1024)

def _read_csv(file: BinaryIO) -> pd.DataFrame:
    file.seek(0)
    return pd.read_csv(file)

def save_uploaded_csv(upload: UploadFile) -> UploadResult:
    dataset_id = str(uuid.uuid4())
    path = RAW_DATA_DIR / f"{dataset_id}.csv"
    tmp_path = RAW_DATA_DIR / f"{dataset_id}.csv.tmp"

    if upload.filename and not upload.filename.lower().endswith(".csv"):
        raise ValueError("Only .csv files are supported")

    size_mb = _get_file_size_mb(upload.file)
    if size_mb > MAX_UPLOAD_MB:
        raise ValueError(f"File too large: {size_mb:.2f} MB (max {MAX_UPLOAD_MB} MB)")

    df = _read_csv(upload.file)
    df = validate_dataset(df, REQUIRED_COLUMNS)

    if len(df) > MAX_ROWS:
        raise ValueError(f"Too many rows: {len(df)} (max {MAX_ROWS})")

    df.to_csv(tmp_path, index=False)
    tmp_path.replace(path)

    logger.info("Uploaded dataset saved", extra={"dataset_id": dataset_id, "rows": len(df)})
    return UploadResult(dataset_id=dataset_id, rows=len(df))

def load_dataset(dataset_id: str) -> pd.DataFrame:
    try:
        uuid.UUID(dataset_id)
    except ValueError as exc:
        raise ValueError("Invalid dataset_id format") from exc

    path = RAW_DATA_DIR / f"{dataset_id}.csv"
    if not path.exists():
        raise FileNotFoundError("Dataset not found")

    df = pd.read_csv(path)
    return validate_dataset(df, REQUIRED_COLUMNS)
