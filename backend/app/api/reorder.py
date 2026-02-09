from fastapi import APIRouter, HTTPException
from app.schemas import ReorderRequest, ReorderResponse
from app.services.data_service import load_dataset
from app.services.inventory_service import calculate_reorder_point

router = APIRouter()

@router.post("/reorder", response_model=ReorderResponse)
def recommend_reorder(req: ReorderRequest):
    try:
        df = load_dataset(req.dataset_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    mean = df["demand"].mean()
    std = df["demand"].std()

    rp, ss = calculate_reorder_point(
        mean, std, req.lead_time_days, req.service_level
    )

    return {
        "reorder_point": rp,
        "safety_stock": ss,
        "recommended_order_qty": max(0, rp - req.current_inventory),
    }
