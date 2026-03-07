import random
import numpy as np
from datetime import datetime, timedelta

# 20 real Delhi wards with approximate coordinates
DELHI_WARDS = [
    {"id": "W001", "name": "Connaught Place", "lat": 28.6315, "lon": 77.2167},
    {"id": "W002", "name": "Karol Bagh", "lat": 28.6514, "lon": 77.1907},
    {"id": "W003", "name": "Lajpat Nagar", "lat": 28.5677, "lon": 77.2436},
    {"id": "W004", "name": "Saket", "lat": 28.5245, "lon": 77.2066},
    {"id": "W005", "name": "Rohini", "lat": 28.7495, "lon": 77.0594},
    {"id": "W006", "name": "Dwarka", "lat": 28.5921, "lon": 77.0460},
    {"id": "W007", "name": "Janakpuri", "lat": 28.6289, "lon": 77.0823},
    {"id": "W008", "name": "Pitampura", "lat": 28.7066, "lon": 77.1302},
    {"id": "W009", "name": "Mayur Vihar", "lat": 28.6074, "lon": 77.2950},
    {"id": "W010", "name": "Shahdara", "lat": 28.6733, "lon": 77.2882},
    {"id": "W011", "name": "Chandni Chowk", "lat": 28.6506, "lon": 77.2303},
    {"id": "W012", "name": "Paharganj", "lat": 28.6448, "lon": 77.2167},
    {"id": "W013", "name": "Vasant Kunj", "lat": 28.5205, "lon": 77.1574},
    {"id": "W014", "name": "Greater Kailash", "lat": 28.5393, "lon": 77.2352},
    {"id": "W015", "name": "Narela", "lat": 28.8527, "lon": 77.0935},
    {"id": "W016", "name": "Mustafabad", "lat": 28.7206, "lon": 77.2888},
    {"id": "W017", "name": "Okhla", "lat": 28.5355, "lon": 77.2720},
    {"id": "W018", "name": "Wazirpur", "lat": 28.6976, "lon": 77.1629},
    {"id": "W019", "name": "Tilak Nagar", "lat": 28.6390, "lon": 77.0953},
    {"id": "W020", "name": "Sangam Vihar", "lat": 28.5033, "lon": 77.2501},
]

DELHI_HOLIDAYS = [
    "2024-01-26", "2024-03-25", "2024-04-14", "2024-08-15",
    "2024-10-02", "2024-10-12", "2024-11-01", "2024-12-25",
    "2025-01-26", "2025-03-14", "2025-04-14", "2025-08-15",
]

def generate_collection_points():
    points = []
    for ward in DELHI_WARDS:
        for i in range(3):
            lat_offset = random.uniform(-0.01, 0.01)
            lon_offset = random.uniform(-0.01, 0.01)
            points.append({
                "name": f"{ward['name']} Point {i+1}",
                "ward_id": ward["id"],
                "ward_name": ward["name"],
                "latitude": ward["lat"] + lat_offset,
                "longitude": ward["lon"] + lon_offset,
                "max_capacity_liters": random.choice([300, 500, 750, 1000]),
                "current_fill_level": round(random.uniform(10, 95), 1),
            })
    return points

def generate_waste_history(days=180):
    history = []
    base_date = datetime.now() - timedelta(days=days)
    for day in range(days):
        current_date = base_date + timedelta(days=day)
        date_str = current_date.strftime("%Y-%m-%d")
        is_holiday = 1 if date_str in DELHI_HOLIDAYS else 0
        day_of_week = current_date.weekday()
        for ward in DELHI_WARDS:
            base_volume = random.uniform(800, 2500)
            if day_of_week >= 5:
                base_volume *= 1.2
            if is_holiday:
                base_volume *= 1.4
            month = current_date.month
            if month in [10, 11]:
                base_volume *= 1.3
            noise = np.random.normal(0, 50)
            volume = max(200, base_volume + noise)
            history.append({
                "ward_id": ward["id"],
                "ward_name": ward["name"],
                "recorded_date": current_date,
                "actual_volume_kg": round(volume, 2),
                "temperature_celsius": round(random.uniform(15, 42), 1),
                "humidity_pct": round(random.uniform(30, 90), 1),
                "is_holiday": is_holiday,
            })
    return history

def generate_citizens(count=100):
    first_names = ["Amit", "Priya", "Rahul", "Sunita", "Vikram", "Anjali", "Rohit", "Kavya",
                   "Deepak", "Neha", "Sanjay", "Pooja", "Arun", "Meena", "Rajesh", "Divya"]
    last_names = ["Sharma", "Gupta", "Singh", "Kumar", "Verma", "Agarwal", "Yadav", "Joshi"]
    citizens = []
    for i in range(count):
        ward = random.choice(DELHI_WARDS)
        points = random.randint(0, 2500)
        tier = "Bronze"
        if points >= 2000:
            tier = "Platinum"
        elif points >= 1000:
            tier = "Gold"
        elif points >= 500:
            tier = "Silver"
        citizens.append({
            "name": f"{random.choice(first_names)} {random.choice(last_names)}",
            "ward_id": ward["id"],
            "ward_name": ward["name"],
            "total_points": points,
            "tier": tier,
        })
    return citizens

def generate_waste_classifications():
    classifications = []
    points = generate_collection_points()
    for point in points:
        organic = random.uniform(20, 60)
        plastic = random.uniform(10, 30)
        paper = random.uniform(5, 20)
        metal = random.uniform(2, 10)
        glass = random.uniform(2, 8)
        hazardous = random.uniform(1, 5)
        total = organic + plastic + paper + metal + glass + hazardous
        classifications.append({
            "ward_id": point["ward_id"],
            "organic_pct": round(organic/total*100, 2),
            "plastic_pct": round(plastic/total*100, 2),
            "paper_pct": round(paper/total*100, 2),
            "metal_pct": round(metal/total*100, 2),
            "glass_pct": round(glass/total*100, 2),
            "hazardous_pct": round(hazardous/total*100, 2),
            "total_volume_liters": round(random.uniform(50, 450), 1),
            "confidence_score": round(random.uniform(0.75, 0.98), 3),
        })
    return classifications
