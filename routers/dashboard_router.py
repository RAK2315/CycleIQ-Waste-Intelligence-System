from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from models.waste_model import WasteClassification, CollectionPoint
from models.citizen_model import Citizen
from ml.llm_engine import query_llm, get_suggested_queries

router = APIRouter()

class QueryRequest(BaseModel):
    message: str

@router.post("/query")
def ask_dashboard(req: QueryRequest, db: Session = Depends(get_db)):
    points = db.query(CollectionPoint).all()
    avg_fill = sum(p.current_fill_level for p in points) / len(points) if points else 0

    # Build ward-level fill summary
    ward_fills = {}
    for p in points:
        if p.ward_name not in ward_fills:
            ward_fills[p.ward_name] = []
        ward_fills[p.ward_name].append(p.current_fill_level)
    ward_avg_fills = {w: round(sum(v)/len(v), 1) for w, v in ward_fills.items()}
    sorted_wards = sorted(ward_avg_fills.items(), key=lambda x: x[1])
    lowest_wards = [f"{w} ({f}%)" for w, f in sorted_wards[:3]]
    highest_wards = [f"{w} ({f}%)" for w, f in sorted_wards[-3:][::-1]]

    citizens = db.query(Citizen).all()
    gold_count = sum(1 for c in citizens if c.tier == "Gold")
    silver_count = sum(1 for c in citizens if c.tier == "Silver")
    platinum_count = sum(1 for c in citizens if c.tier == "Platinum")
    bronze_count = sum(1 for c in citizens if c.tier == "Bronze")

    context = {
        "total_collection_points": len(points),
        "avg_fill_level_pct": round(avg_fill, 1),
        "highest_fill_wards": highest_wards,
        "lowest_fill_wards": lowest_wards,
        "total_citizens": len(citizens),
        "platinum_citizens": platinum_count,
        "gold_citizens": gold_count,
        "silver_citizens": silver_count,
        "bronze_citizens": bronze_count,
        "total_classifications": db.query(WasteClassification).count(),
        "wards_monitored": len(ward_fills),
        "high_priority_points": len([p for p in points if p.current_fill_level > 75]),
    }
    response = query_llm(req.message, context)
    return {"query": req.message, "response": response}

@router.get("/suggested-queries")
def suggested_queries():
    return get_suggested_queries()

@router.get("/summary")
def get_summary(db: Session = Depends(get_db)):
    points = db.query(CollectionPoint).all()
    avg_fill = sum(p.current_fill_level for p in points) / len(points) if points else 0
    return {
        "total_wards": len(set(p.ward_id for p in points)),
        "total_collection_points": len(points),
        "avg_fill_level": round(avg_fill, 1),
        "high_priority_points": len([p for p in points if p.current_fill_level > 75]),
        "total_citizens": db.query(Citizen).count(),
        "total_classifications": db.query(WasteClassification).count(),
    }
