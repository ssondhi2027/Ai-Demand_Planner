from fastapi import APIRouter, HTTPException
from app.schemas import ForecastRequest, ForecastResponse, HistoryResponse
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

@router.get("/history", response_model=HistoryResponse)
def history(dataset_id: str, limit: int = 180):
    try:
        df = load_dataset(dataset_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    df = df.sort_values("date")
    if limit > 0:
        df = df.tail(limit)

    return {
        "dates": df["date"].astype(str).tolist(),
        "demand": df["demand"].astype(float).tolist()
    }
