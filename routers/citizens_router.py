from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from models.citizen_model import Citizen, CitizenActivity
import uuid, random
from datetime import datetime

router = APIRouter()

class CitizenCreate(BaseModel):
    name: str
    ward_id: str
    ward_name: str

class ActivityLog(BaseModel):
    citizen_id: str
    action_type: str  # proper_segregation, recycling_drop_off, bulk_waste_report, community_cleanup
    ward_id: str

POINTS_MAP = {
    "proper_segregation": 50,
    "recycling_drop_off": 75,
    "bulk_waste_report": 30,
    "community_cleanup": 100,
}

def get_tier(points: int) -> str:
    if points >= 2000: return "Platinum"
    elif points >= 1000: return "Gold"
    elif points >= 500: return "Silver"
    return "Bronze"

@router.get("/leaderboard")
def get_leaderboard(ward_id: str = None, limit: int = 20, db: Session = Depends(get_db)):
    query = db.query(Citizen)
    if ward_id:
        query = query.filter(Citizen.ward_id == ward_id)
    citizens = query.order_by(Citizen.total_points.desc()).limit(limit).all()
    return [{"rank": i+1, "name": c.name, "ward": c.ward_name,
             "points": c.total_points, "tier": c.tier} for i, c in enumerate(citizens)]

@router.post("/register")
def register_citizen(data: CitizenCreate, db: Session = Depends(get_db)):
    citizen = Citizen(id=str(uuid.uuid4()), name=data.name,
                      ward_id=data.ward_id, ward_name=data.ward_name,
                      total_points=0, tier="Bronze")
    db.add(citizen)
    db.commit()
    return {"id": citizen.id, "message": f"Welcome to CycleIQ, {data.name}!"}

@router.post("/activity")
def log_activity(data: ActivityLog, db: Session = Depends(get_db)):
    citizen = db.query(Citizen).filter(Citizen.id == data.citizen_id).first()
    if not citizen:
        return {"error": "Citizen not found"}
    points = POINTS_MAP.get(data.action_type, 25)
    activity = CitizenActivity(id=str(uuid.uuid4()), citizen_id=data.citizen_id,
                                action_type=data.action_type, points_earned=points,
                                ward_id=data.ward_id)
    db.add(activity)
    citizen.total_points += points
    citizen.tier = get_tier(citizen.total_points)
    db.commit()
    return {"points_earned": points, "total_points": citizen.total_points, "tier": citizen.tier}

@router.get("/stats")
def citizen_stats(db: Session = Depends(get_db)):
    citizens = db.query(Citizen).all()
    if not citizens:
        return {}
    tiers = {"Bronze": 0, "Silver": 0, "Gold": 0, "Platinum": 0}
    for c in citizens:
        tiers[c.tier] = tiers.get(c.tier, 0) + 1
    return {
        "total_citizens": len(citizens),
        "total_points_awarded": sum(c.total_points for c in citizens),
        "avg_points": round(sum(c.total_points for c in citizens) / len(citizens), 1),
        "tier_distribution": tiers,
        "top_citizen": max(citizens, key=lambda c: c.total_points).name if citizens else None
    }
