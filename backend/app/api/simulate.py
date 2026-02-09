from fastapi import APIRouter
from app.schemas import SimulationRequest
from app.services.data_service import load_dataset
from ..services.forecasting_service import forecast_demand
from app.services.simulation_service import simulate_stockout

router = APIRouter()

@router.post("/simulate")
def simulate(req: SimulationRequest):
    df = load_dataset(req.dataset_id)
    _, forecast, _, _ = forecast_demand(df)

    prob, days, risk = simulate_stockout(
        forecast, req.current_inventory, req.simulations
    )

    return {
        "stockout_probability": prob,
        "expected_stockout_days": days,
        "risk_level": risk,
    }

def SimulationRequest(
        demand_multiplier: float = 1.0,
        lead_time_days: int = 7,
):
    return {
        "demand_multiplier": demand_multiplier,
        "lead_time_days": lead_time_days,
    }