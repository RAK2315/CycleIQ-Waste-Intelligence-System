from sqlalchemy import Column, String, Float, DateTime, Integer, JSON
from sqlalchemy.sql import func
from database import Base
import uuid

class CollectionPoint(Base):
    __tablename__ = "collection_points"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    ward_id = Column(String, nullable=False)
    ward_name = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    max_capacity_liters = Column(Float, default=500.0)
    current_fill_level = Column(Float, default=0.0)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, server_default=func.now())

class WasteClassification(Base):
    __tablename__ = "waste_classifications"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    collection_point_id = Column(String, nullable=False)
    ward_id = Column(String, nullable=False)
    organic_pct = Column(Float, default=0.0)
    plastic_pct = Column(Float, default=0.0)
    paper_pct = Column(Float, default=0.0)
    metal_pct = Column(Float, default=0.0)
    glass_pct = Column(Float, default=0.0)
    hazardous_pct = Column(Float, default=0.0)
    total_volume_liters = Column(Float, default=0.0)
    confidence_score = Column(Float, default=0.0)
    image_path = Column(String, nullable=True)
    classified_at = Column(DateTime, server_default=func.now())
