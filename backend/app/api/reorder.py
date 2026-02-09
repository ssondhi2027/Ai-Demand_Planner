from fastapi import APIRouter
from app.schemas import ReorderRequest
from app.services.data_service import load_dataset
from app.services.inventory_service import calculate_reorder_point

router = APIRouter()

@router.post("/reorder")
def recommend_reorder(req: ReorderRequest):
    df = load_dataset(req.dataset_id)
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