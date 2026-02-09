import logging
import os
from fastapi import FastAPI
from app.api import upload, forecast, reorder, simulate

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

app = FastAPI(title="AI Demand Planning API")

@app.get("/")
def health_check():
    return {"status": "API is running"}

#--- CORS Middleware (if needed) ---
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3001",
        "http://localhost:3003",
        "http://localhost:5173",   # default Vite port (IMPORTANT)
        "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#--- Include Routers ---  

app.include_router(upload.router, prefix="/api/upload", tags=["Upload"])
app.include_router(forecast.router, prefix="/api/forecast", tags=["Forecast"])
app.include_router(reorder.router, prefix="/api/reorder", tags=["Reorder"])
app.include_router(simulate.router, prefix="/api/simulate", tags=["Simulate"])
