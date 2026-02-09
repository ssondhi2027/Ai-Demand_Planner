# from fastapi import APIRouter
# from app.services.data_service import load_dataset
# from app.services.forecasting_service import forecast_demand
# from fastapi import HTTPException

# router = APIRouter()

# @router.post("/forecast", operation_id="generate_forecast")
# def forecast(dataset_id: str, model: str = "arima"):
#     df = load_dataset(dataset_id)

#     if df.empty:
#         raise HTTPException(status_code=400, detail="Dataset is empty")
    
#     if "demand" not in df.columns:
#         raise HTTPException(status_code=400, detail="Dataset must contain 'demand' column")
#     dates, forecast, lower, upper = forecast_demand(df)

#     if model == "arima":
#         # ARIMA-specific adjustments (if any)
#         pass

#     if model == "xgboost":
#         # XGBoost-specific adjustments (if any)
#         pass

#     return {
#         "dates": dates.astype(str).tolist(),
#         "forecast": forecast.tolist(),
#         "lower": lower.tolist(),
#         "upper": upper.tolist(),
#     }

# @router.post("/forecast")
# def forecast(dataset_id: str):
#     df = load_dataset(dataset_id)

#     if df.empty:
#         raise HTTPException(status_code=400, detail="Dataset is empty")
    
#     if "demand" not in df.columns:
#         raise HTTPException(status_code=400, detail="Dataset must contain 'demand' column")

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.data_service import load_dataset
from app.services.forecasting_service import (
    forecast_arima,
    forecast_xgboost
)

router = APIRouter()

class ForecastRequest(BaseModel):
    dataset_id: str
    model: str = "arima"
    horizon: int = 30

@router.post("/forecast", operation_id="generate_forecast")
def forecast(req: ForecastRequest):
    df = load_dataset(req.dataset_id)

    if df.empty:
        raise HTTPException(status_code=400, detail="Dataset is empty")

    if "demand" not in df.columns or "date" not in df.columns:
        raise HTTPException(
            status_code=400,
            detail="Dataset must contain 'date' and 'demand' columns"
        )

    if req.model == "arima":
        result = forecast_arima(df, req.horizon)

    elif req.model == "xgboost":
        result = forecast_xgboost(df, req.horizon)

    else:
        raise HTTPException(status_code=400, detail="Unsupported model")

    return result
