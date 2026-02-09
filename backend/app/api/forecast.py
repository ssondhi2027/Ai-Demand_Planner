from fastapi import APIRouter, HTTPException
from app.schemas import ForecastRequest, ForecastResponse
from app.services.data_service import load_dataset
from app.services.forecasting_service import forecast_arima, forecast_xgboost

router = APIRouter()

@router.post("/forecast", operation_id="generate_forecast", response_model=ForecastResponse)
def forecast(req: ForecastRequest):
    try:
        df = load_dataset(req.dataset_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    try:
        if req.model == "arima":
            return forecast_arima(df, req.horizon)
        if req.model == "xgboost":
            return forecast_xgboost(df, req.horizon)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    raise HTTPException(status_code=400, detail="Unsupported model")
