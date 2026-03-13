from fastapi import APIRouter, Depends, UploadFile, File
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models.waste_model import WasteClassification, CollectionPoint
from models.citizen_model import Citizen
from ml.cv_module import classifier
import uuid

router = APIRouter()

@router.get("/collection-points")
def get_collection_points(db: Session = Depends(get_db)):
    points = db.query(CollectionPoint).filter(CollectionPoint.is_active == 1).all()
    return [{"id": p.id, "name": p.name, "ward_id": p.ward_id, "ward_name": p.ward_name,
             "latitude": p.latitude, "longitude": p.longitude,
             "fill_level": p.current_fill_level, "max_capacity": p.max_capacity_liters} for p in points]

@router.get("/classifications")
def get_classifications(limit: int = 100, db: Session = Depends(get_db)):
    items = db.query(WasteClassification).order_by(WasteClassification.classified_at.desc()).limit(limit).all()
    return items

@router.get("/ward-summary")
def get_ward_summary(db: Session = Depends(get_db)):
    results = db.query(
        WasteClassification.ward_id,
        func.avg(WasteClassification.organic_pct).label("avg_organic"),
        func.avg(WasteClassification.plastic_pct).label("avg_plastic"),
        func.avg(WasteClassification.paper_pct).label("avg_paper"),
        func.avg(WasteClassification.metal_pct).label("avg_metal"),
        func.avg(WasteClassification.glass_pct).label("avg_glass"),
        func.avg(WasteClassification.hazardous_pct).label("avg_hazardous"),
        func.avg(WasteClassification.total_volume_liters).label("avg_volume"),
        func.count(WasteClassification.id).label("total_classifications"),
    ).group_by(WasteClassification.ward_id).all()
    return [dict(r._mapping) for r in results]

@router.post("/classify")
async def classify_image(
    file: UploadFile = File(...),
    collection_point_id: str = "",
    ward_id: str = "W001",
    # Optional overrides from live camera — if provided, skip CV inference
    organic_pct: Optional[float] = None,
    plastic_pct: Optional[float] = None,
    paper_pct: Optional[float] = None,
    metal_pct: Optional[float] = None,
    glass_pct: Optional[float] = None,
    hazardous_pct: Optional[float] = None,
    db: Session = Depends(get_db)
):
    image_bytes = await file.read()

    # Live camera sends pre-computed pcts — use them directly
    if organic_pct is not None:
        result = {
            "organic_pct": organic_pct,
            "plastic_pct": plastic_pct or 0.0,
            "paper_pct": paper_pct or 0.0,
            "metal_pct": metal_pct or 0.0,
            "glass_pct": glass_pct or 0.0,
            "hazardous_pct": hazardous_pct or 0.0,
            "total_volume_liters": 100.0,
            "confidence_score": 0.88,
            "mode": "live-camera",
            "note": "Captured from live webcam stream"
        }
    else:
        result = classifier.classify_image(image_bytes)

    db_fields = {
        "organic_pct": result["organic_pct"],
        "plastic_pct": result["plastic_pct"],
        "paper_pct": result["paper_pct"],
        "metal_pct": result["metal_pct"],
        "glass_pct": result["glass_pct"],
        "hazardous_pct": result["hazardous_pct"],
        "total_volume_liters": result.get("total_volume_liters", 100.0),
        "confidence_score": result["confidence_score"],
    }
    classification = WasteClassification(
        id=str(uuid.uuid4()),
        collection_point_id=collection_point_id or str(uuid.uuid4()),
        ward_id=ward_id,
        **db_fields
    )

    segregation_score = _calc_segregation_score(result)
    result["segregation_score"] = segregation_score
    result["segregation_label"] = _score_label(segregation_score)

    points_awarded = 0
    if segregation_score >= 70:
        points_awarded = int(segregation_score / 10) * 10
        citizens = db.query(Citizen).filter(Citizen.ward_id == ward_id).all()
        for citizen in citizens[:5]:
            citizen.total_points += points_awarded // 5
            citizen.tier = _get_tier(citizen.total_points)

    if collection_point_id:
        point = db.query(CollectionPoint).filter(CollectionPoint.id == collection_point_id).first()
        if point:
            point.current_fill_level = min(100, point.current_fill_level + result.get("total_volume_liters", 50) / point.max_capacity_liters * 100)

    db.add(classification)
    db.commit()

    result["saved"] = True
    result["points_awarded_to_ward"] = points_awarded
    result["ward_id"] = ward_id
    return result

def _calc_segregation_score(result: dict) -> float:
    pcts = [result.get("organic_pct",0), result.get("plastic_pct",0),
            result.get("paper_pct",0), result.get("metal_pct",0),
            result.get("glass_pct",0), result.get("hazardous_pct",0)]
    dominant = max(pcts)
    hazardous = result.get("hazardous_pct", 0)
    score = (dominant / 100) * 80 + (1 - hazardous / 100) * 20
    return round(score, 1)

def _score_label(score: float) -> str:
    if score >= 80: return "Excellent"
    elif score >= 65: return "Good"
    elif score >= 50: return "Fair"
    return "Poor"

def _get_tier(points: int) -> str:
    if points >= 2000: return "Platinum"
    elif points >= 1000: return "Gold"
    elif points >= 500: return "Silver"
    return "Bronze"

@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    total = db.query(WasteClassification).count()
    points = db.query(CollectionPoint).all()
    avg_fill = sum(p.current_fill_level for p in points) / len(points) if points else 0
    high_fill = [p for p in points if p.current_fill_level > 75]
    return {
        "total_classifications": total,
        "total_collection_points": len(points),
        "avg_fill_level": round(avg_fill, 1),
        "high_fill_count": len(high_fill),
        "active_points": len([p for p in points if p.is_active])
    }

@router.post("/update-fill/{point_id}")
def update_fill_level(point_id: str, fill_level: float, db: Session = Depends(get_db)):
    point = db.query(CollectionPoint).filter(CollectionPoint.id == point_id).first()
    if point:
        point.current_fill_level = min(100, max(0, fill_level))
        db.commit()
        return {"success": True, "new_fill": point.current_fill_level}
    return {"success": False}