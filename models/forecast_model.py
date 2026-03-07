from sqlalchemy import Column, String, Float, DateTime, Integer
from sqlalchemy.sql import func
from database import Base
import uuid

class WasteForecast(Base):
    __tablename__ = "waste_forecasts"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    ward_id = Column(String, nullable=False)
    ward_name = Column(String, nullable=False)
    forecast_date = Column(DateTime, nullable=False)
    predicted_volume_kg = Column(Float, nullable=False)
    lower_bound_kg = Column(Float, nullable=False)
    upper_bound_kg = Column(Float, nullable=False)
    confidence_score = Column(Float, nullable=False)
    model_used = Column(String, default="prophet")
    created_at = Column(DateTime, server_default=func.now())

class WasteHistory(Base):
    __tablename__ = "waste_history"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    ward_id = Column(String, nullable=False)
    ward_name = Column(String, nullable=False)
    recorded_date = Column(DateTime, nullable=False)
    actual_volume_kg = Column(Float, nullable=False)
    temperature_celsius = Column(Float, nullable=True)
    humidity_pct = Column(Float, nullable=True)
    is_holiday = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
