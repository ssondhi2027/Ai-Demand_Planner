from fastapi import APIRouter, UploadFile, File, HTTPException
from app.schemas import UploadResponse
from app.services.data_service import save_uploaded_csv

router = APIRouter()

@router.post("/upload", response_model=UploadResponse)
def upload_csv(file: UploadFile = File(...)):
    try:
        result = save_uploaded_csv(file)
        return {"dataset_id": result.dataset_id, "rows": result.rows}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
