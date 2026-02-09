from pydantic import BaseModel, Field
from typing import List, Literal

class UploadResponse(BaseModel):
    dataset_id: str
    rows: int

class ForecastRequest(BaseModel):
    dataset_id: str
    model: Literal["arima", "xgboost"] = "arima"
    horizon: int = Field(30, ge=1, le=365)

class ForecastResponse(BaseModel):
    model: str
    dates: List[str]
    forecast: List[float]
    lower: List[float]
    upper: List[float]
    metrics: dict | None = None

class ReorderRequest(BaseModel):
    dataset_id: str
    lead_time_days: int = Field(..., ge=1, le=365)
    service_level: float = Field(..., gt=0, le=1)
    current_inventory: int = Field(..., ge=0)

class ReorderResponse(BaseModel):
    reorder_point: int
    safety_stock: int
    recommended_order_qty: int

class SimulationRequest(BaseModel):
    dataset_id: str
    current_inventory: int = Field(..., ge=0)
    simulations: int = Field(1000, ge=10, le=100000)
    model: Literal["arima", "xgboost"] = "arima"
    horizon: int = Field(30, ge=1, le=365)

class SimulationResponse(BaseModel):
    stockout_probability: float
    expected_stockout_days: float
    risk_level: str
