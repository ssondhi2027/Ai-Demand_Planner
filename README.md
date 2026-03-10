# AI Demand Planner

A portfolio-ready demand forecasting backend + frontend demo.  
Upload historical demand data, run ARIMA and XGBoost forecasts, and compare results in a clean visual dashboard.

## Purpose
- Demonstrate production-minded backend design for ML forecasting.
- Showcase a modern React frontend tied to FastAPI.
- Provide a clear end-to-end flow: authentication gate -> data upload -> model comparison.

## Tech Stack
- Backend: FastAPI, Pandas, Statsmodels, XGBoost, scikit-learn
- Frontend: React + Vite + Recharts
- Language: Python + TypeScript

## Setup

### 1) Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend default URL: `http://127.0.0.1:8000`

### 2) Frontend
```bash
cd frontend
npm install
npm run dev
```

Frontend default URL: `http://localhost:5173`

If your backend runs on another host/port, set:
```bash
set VITE_API_BASE=http://127.0.0.1:8000
```

## CSV Format
Your CSV must include the following columns:
- `date` (YYYY-MM-DD recommended)
- `product_id`
- `demand` (numeric, non-negative)

Note: Forecasts aggregate demand across all products in the uploaded file.

## Working Flow
1. Open the frontend.
2. Complete the authenticity gate (demo UI only).
3. Upload a CSV.
4. Backend validates and stores the dataset.
5. Frontend requests ARIMA and XGBoost forecasts.
6. Results are displayed on the dashboard with confidence bands.

## API Endpoints (Backend)
- `POST /api/upload/upload`  
  Upload a CSV, returns `dataset_id` and row count.
- `POST /api/forecast/forecast`  
  Body: `{ dataset_id, model, horizon }`  
  Models: `"arima" | "xgboost"`
- `POST /api/reorder/reorder`  
  Calculates reorder point and safety stock.
- `POST /api/simulate/simulate`  
  Monte Carlo stockout simulation using forecast output.

## Pseudocode

### Upload
```
on POST /api/upload/upload:
  read CSV
  validate required columns and data types
  enforce size and row limits
  save to data/raw/<dataset_id>.csv
  return dataset_id and row count
```

### Forecast (ARIMA)
```
on POST /api/forecast/forecast with model=arima:
  load dataset by dataset_id
  validate dataset
  build datetime index with frequency
  fit ARIMA(1,1,1)
  forecast horizon
  return forecast + confidence intervals
```

### Forecast (XGBoost)
```
on POST /api/forecast/forecast with model=xgboost:
  load dataset by dataset_id
  validate dataset
  build lag/rolling features
  train XGBoost regressor
  recursively predict horizon
  compute residual-based confidence bands
  return forecast + metrics (MAE/RMSE)
```

### Reorder Recommendation
```
on POST /api/reorder/reorder:
  load dataset
  compute mean and std of demand
  safety_stock = z(service_level) * std * sqrt(lead_time)
  reorder_point = mean * lead_time + safety_stock
  return reorder_point and recommended order quantity
```

### Simulation
```
on POST /api/simulate/simulate:
  load dataset
  run forecast with chosen model
  simulate inventory depletion over forecast horizon
  return stockout probability and risk level
```

## Notes
- This is a portfolio demo with production-style validation and error handling.
- For real production use, add persistence (S3/DB), auth, and monitoring.
