from fastapi import APIRouter, UploadFile, File
from app.services.data_service import save_uploaded_csv

router = APIRouter()

@router.post("/upload")
def upload_csv(file: UploadFile = File(...)):
    dataset_id, rows = save_uploaded_csv(file.file)
    return {"dataset_id": dataset_id, "rows": rows}