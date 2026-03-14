from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from database import init_db
from routers import waste_router as waste, forecast_router as forecast, routes_router as routes, dashboard_router as dashboard, citizens_router as citizens
import asyncio, random

load_dotenv()

app = FastAPI(title="CycleIQ API", version="1.0.0")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])

app.include_router(waste.router, prefix="/api/waste", tags=["Waste"])
app.include_router(forecast.router, prefix="/api/forecast", tags=["Forecast"])
app.include_router(routes.router, prefix="/api/routes", tags=["Routes"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(citizens.router, prefix="/api/citizens", tags=["Citizens"])

@app.on_event("startup")
async def startup():
    init_db()
    await seed_data()
    asyncio.create_task(iot_simulation_loop())

async def iot_simulation_loop():
    await asyncio.sleep(10)
    from database import SessionLocal
    from models.waste_model import CollectionPoint
    print("IoT simulation loop started — updating fill levels every 30s")
    while True:
        try:
            db = SessionLocal()
            points = db.query(CollectionPoint).all()
            sample = random.sample(points, max(1, len(points) // 5))
            for point in sample:
                if point.current_fill_level > 80:
                    delta = random.uniform(-40, -20)
                elif point.current_fill_level > 50:
                    delta = random.uniform(-3, 8)
                else:
                    delta = random.uniform(1, 6)
                point.current_fill_level = max(5, min(98, point.current_fill_level + delta))
            db.commit()
            db.close()
        except Exception as e:
            print(f"IoT sim error: {e}")
        await asyncio.sleep(30)

async def seed_data():
    from database import SessionLocal
    from models.waste_model import CollectionPoint, WasteClassification
    from models.forecast_model import WasteHistory
    from models.citizen_model import Citizen
    from data.synthetic_data import generate_collection_points, generate_waste_history, generate_citizens
    import uuid

    db = SessionLocal()
    try:
        if db.query(CollectionPoint).count() == 0:
            print("Seeding database...")
            for cp in generate_collection_points():
                db.add(CollectionPoint(id=str(uuid.uuid4()), **cp))
            db.commit()
        else:
            import numpy as np
            pts = db.query(CollectionPoint).all()
            for pt in pts:
                pt.current_fill_level = round(np.random.uniform(10, 85), 1)
            db.commit()

        if db.query(WasteHistory).count() == 0:
            for h in generate_waste_history(180):
                db.add(WasteHistory(id=str(uuid.uuid4()), **h))
            db.commit()

        if db.query(WasteClassification).count() == 0:
            from data.synthetic_data import generate_waste_classifications
            pts = db.query(CollectionPoint).all()
            clsfs = generate_waste_classifications()
            for i, pt in enumerate(pts):
                s = clsfs[i % len(clsfs)]
                db.add(WasteClassification(
                    id=str(uuid.uuid4()),
                    collection_point_id=pt.id,
                    ward_id=pt.ward_id,
                    organic_pct=s["organic_pct"], plastic_pct=s["plastic_pct"],
                    paper_pct=s["paper_pct"], metal_pct=s["metal_pct"],
                    glass_pct=s["glass_pct"], hazardous_pct=s["hazardous_pct"],
                    total_volume_liters=s.get("total_volume_liters", 100.0),
                    confidence_score=s["confidence_score"],
                ))
            db.commit()

        if db.query(Citizen).count() == 0:
            for c in generate_citizens(150):
                db.add(Citizen(id=str(uuid.uuid4()), **c))
            db.commit()

        print("Database seeded successfully.")
    except Exception as e:
        print(f"Seeding error: {e}")
        db.rollback()
    finally:
        db.close()

@app.get("/")
@app.head("/")
def root():
    return {"message": "CycleIQ API running", "version": "1.0.0"}

@app.get("/health")
@app.head("/health")
def health():
    return {"status": "healthy"}

@app.head("/api/dashboard/summary")
async def head_summary():
    return {}