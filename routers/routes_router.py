from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.waste_model import CollectionPoint
from models.citizen_model import OptimizedRoute
from ml.route_optimizer import optimize_routes
import uuid
from datetime import datetime

router = APIRouter()

@router.get("/optimize")
def get_optimized_routes(num_trucks: int = 3, db: Session = Depends(get_db)):
    points = db.query(CollectionPoint).filter(CollectionPoint.is_active == 1).all()
    point_data = [{"id": p.id, "name": p.name, "ward_id": p.ward_id, "ward_name": p.ward_name,
                   "latitude": p.latitude, "longitude": p.longitude,
                   "current_fill_level": p.current_fill_level} for p in points]
    routes = optimize_routes(point_data, num_trucks)
    saved = []
    for r in routes:
        normalized_seq = [
            {"name": s["name"], "ward": s["ward_name"],
             "lat": s["latitude"], "lon": s["longitude"],
             "fill_level": s.get("current_fill_level", s.get("fill_level", 70))}
            for s in r["collection_sequence"]
        ]
        route = OptimizedRoute(
            id=str(uuid.uuid4()),
            truck_id=r["truck_id"],
            route_date=datetime.now(),
            collection_sequence=normalized_seq,
            total_distance_km=r["total_distance_km"],
            estimated_time_minutes=r["estimated_time_minutes"],
            estimated_emissions_kg=r["estimated_emissions_kg"],
            status="planned"
        )
        db.add(route)
        saved.append({
            "truck_id": r["truck_id"],
            "collection_sequence": normalized_seq,
            "total_distance_km": r["total_distance_km"],
            "estimated_time_minutes": r["estimated_time_minutes"],
            "estimated_emissions_kg": r["estimated_emissions_kg"],
            "num_stops": len(normalized_seq),
            "status": "planned"
        })
    db.commit()
    return saved

@router.get("/latest")
def get_latest_routes(db: Session = Depends(get_db)):
    """Returns the most recently optimized routes — same data driver view uses."""
    from sqlalchemy import func
    # Get the most recent batch (routes generated together have close timestamps)
    latest = db.query(OptimizedRoute).order_by(OptimizedRoute.route_date.desc()).first()
    if not latest:
        return []
    # Get all routes from the same batch (within 5 seconds of the latest)
    from datetime import timedelta
    cutoff = latest.route_date - timedelta(seconds=5)
    routes = db.query(OptimizedRoute).filter(
        OptimizedRoute.route_date >= cutoff
    ).order_by(OptimizedRoute.truck_id).all()
    return [{
        "truck_id": r.truck_id,
        "collection_sequence": r.collection_sequence,
        "total_distance_km": r.total_distance_km,
        "estimated_time_minutes": r.estimated_time_minutes,
        "estimated_emissions_kg": r.estimated_emissions_kg,
        "num_stops": len(r.collection_sequence) if r.collection_sequence else 0,
        "status": r.status
    } for r in routes]

@router.get("/stats")
def get_route_stats(db: Session = Depends(get_db)):
    from sqlalchemy import func
    total = db.query(OptimizedRoute).count()
    if total == 0:
        return {"total_routes": 0, "avg_distance_km": 0, "avg_emissions_kg": 0}
    result = db.query(
        func.avg(OptimizedRoute.total_distance_km).label("avg_dist"),
        func.avg(OptimizedRoute.estimated_emissions_kg).label("avg_emissions"),
        func.sum(OptimizedRoute.total_distance_km).label("total_dist"),
    ).first()
    return {
        "total_routes": total,
        "avg_distance_km": round(result.avg_dist or 0, 2),
        "avg_emissions_kg": round(result.avg_emissions or 0, 3),
        "total_distance_km": round(result.total_dist or 0, 2),
        "estimated_savings_pct": 22
    }