from pydantic import BaseModel
from typing import List

class UploadResponse(BaseModel):
    dataset_id: str
    rows: int

class ForecastResponse(BaseModel):
    dates: List[str]
    forecast: List[float]
    lower: List[float]
    upper: List[float]

class ReorderRequest(BaseModel):
    dataset_id: str
    lead_time_days: int
    service_level: float
    current_inventory: int

class ReorderResponse(BaseModel):
    reorder_point: int
    safety_stock: int
    recommended_order_qty: int

class SimulationRequest(BaseModel):
    dataset_id: str
    current_inventory: int
    simulations: int = 1000

class SimulationResponse(BaseModel):
    stockout_probability: float
    expected_stockout_days: float
    risk_level: str