from fastapi import APIRouter, HTTPException
from app.schemas import SimulationRequest, SimulationResponse
from app.services.data_service import load_dataset
from app.services.forecasting_service import forecast_demand
from app.services.simulation_service import simulate_stockout

router = APIRouter()

@router.post("/simulate", response_model=SimulationResponse)
def simulate(req: SimulationRequest):
    try:
        df = load_dataset(req.dataset_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    try:
        result = forecast_demand(df, horizon=req.horizon, model=req.model)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    forecast = result["forecast"]

    prob, days, risk = simulate_stockout(
        forecast, req.current_inventory, req.simulations
    )

    return {
        "stockout_probability": prob,
        "expected_stockout_days": days,
        "risk_level": risk,
    }
