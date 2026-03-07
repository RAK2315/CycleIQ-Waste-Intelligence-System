from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.forecast_model import WasteForecast, WasteHistory
from ml.forecasting import generate_forecast
from data.synthetic_data import DELHI_WARDS
import uuid

router = APIRouter()

@router.get("/ward/{ward_id}")
def get_ward_forecast(ward_id: str, days: int = 7, db: Session = Depends(get_db)):
    ward = next((w for w in DELHI_WARDS if w["id"] == ward_id), None)
    if not ward:
        return {"error": "Ward not found"}
    history = db.query(WasteHistory).filter(WasteHistory.ward_id == ward_id).order_by(WasteHistory.recorded_date).all()
    history_data = [{"recorded_date": h.recorded_date, "actual_volume_kg": h.actual_volume_kg} for h in history]
    forecasts = generate_forecast(ward_id, ward["name"], history_data, days)
    return forecasts

@router.get("/all-wards")
def get_all_wards_forecast(db: Session = Depends(get_db)):
    results = []
    for ward in DELHI_WARDS:
        history = db.query(WasteHistory).filter(WasteHistory.ward_id == ward["id"]).order_by(WasteHistory.recorded_date).all()
        history_data = [{"recorded_date": h.recorded_date, "actual_volume_kg": h.actual_volume_kg} for h in history]
        forecasts = generate_forecast(ward["id"], ward["name"], history_data, 7)
        if forecasts:
            results.append({
                "ward_id": ward["id"],
                "ward_name": ward["name"],
                "next_7_days_avg": round(sum(f["predicted_volume_kg"] for f in forecasts) / len(forecasts), 2),
                "peak_day": max(forecasts, key=lambda x: x["predicted_volume_kg"]),
                "forecasts": forecasts
            })
    return results

@router.get("/history/{ward_id}")
def get_history(ward_id: str, days: int = 30, db: Session = Depends(get_db)):
    from datetime import datetime, timedelta
    cutoff = datetime.now() - timedelta(days=days)
    history = db.query(WasteHistory).filter(
        WasteHistory.ward_id == ward_id,
        WasteHistory.recorded_date >= cutoff
    ).order_by(WasteHistory.recorded_date).all()
    return [{"date": h.recorded_date, "volume_kg": h.actual_volume_kg, "is_holiday": h.is_holiday} for h in history]

@router.get("/wards")
def get_wards():
    return DELHI_WARDS
