from sqlalchemy import Column, String, Float, DateTime, Integer, JSON
from sqlalchemy.sql import func
from database import Base
import uuid

class OptimizedRoute(Base):
    __tablename__ = "optimized_routes"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    truck_id = Column(String, nullable=False)
    route_date = Column(DateTime, nullable=False)
    collection_sequence = Column(JSON, nullable=False)
    total_distance_km = Column(Float, nullable=False)
    estimated_time_minutes = Column(Float, nullable=False)
    estimated_emissions_kg = Column(Float, nullable=False)
    status = Column(String, default="planned")
    created_at = Column(DateTime, server_default=func.now())

class Citizen(Base):
    __tablename__ = "citizens"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    ward_id = Column(String, nullable=False)
    ward_name = Column(String, nullable=False)
    total_points = Column(Integer, default=0)
    tier = Column(String, default="Bronze")
    created_at = Column(DateTime, server_default=func.now())

class CitizenActivity(Base):
    __tablename__ = "citizen_activities"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    citizen_id = Column(String, nullable=False)
    action_type = Column(String, nullable=False)
    points_earned = Column(Integer, nullable=False)
    ward_id = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
