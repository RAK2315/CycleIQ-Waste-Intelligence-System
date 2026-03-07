# CycleIQ — AI-Powered Circular Waste Intelligence for Delhi

> **India Innovates 2026 Hackathon** · Team Sigmoid · JSS University  
> Domain: Urban Solutions · Prize Pool: ₹10,00,000+

---

## The Problem

Delhi generates **11,000 tonnes of waste every day**. Despite a city-wide mandate for source segregation — households are required to separate wet and dry waste — compliance is near zero. Trucks run on fixed schedules regardless of whether bins are full or empty, wasting fuel and manpower. There is no feedback loop: citizens have no reason to segregate properly, and the city has no real-time visibility into what is happening on the ground.

The result: overflowing bins in some wards, unnecessary truck visits in others, recyclable material buried in landfills, and a system that is reactive instead of intelligent.

---

## What CycleIQ Does

CycleIQ is an end-to-end waste intelligence platform that closes the loop between **citizens, bins, trucks, and city planners** using computer vision, IoT simulation, route optimization, and AI forecasting.

The system targets **apartment complexes and community collection points** — shared bin areas where residents drop waste before MCD trucks collect it. This is where Delhi's source segregation mandate is supposed to be enforced, and where CycleIQ intervenes.

---

## How It Works — The Full Story

### 1. Computer Vision at Source
A camera mounted above each community bin collection point watches which bin residents use. Delhi's mandate requires separate green bins (wet/organic) and blue bins (dry/recyclable). The camera does not need to see inside bags — it detects which bin a person opens and whether the waste type matches.

CycleIQ uses **YOLOv8**, a state-of-the-art real-time object detection model, to classify waste as:
- **Biodegradable** — food waste, organic matter
- **Recyclable** — plastic, paper, metal, glass
- **Hazardous** — electronics, batteries, chemicals

A **segregation score** (0–100) is calculated per classification based on how cleanly a single waste type dominates. High scores mean good segregation. Low scores trigger alerts.

### 2. Citizen Incentives Tied to Segregation Quality
When a ward's collection points consistently show high segregation scores, citizens in that ward earn points on the CycleIQ platform. This is community-level gamification — not individual surveillance — creating peer pressure and collective accountability. Citizens can view their ward's leaderboard and track their own contribution.

This directly addresses why source segregation fails in Delhi today: there is no personal benefit to doing it correctly. CycleIQ creates one.

### 3. IoT Fill Level Monitoring
Each bin is equipped with an **ultrasonic sensor** that measures the distance from the sensor to the waste surface, calculating fill percentage. This data is transmitted in real time to the CycleIQ API via GSM or LoRa network.

> In the current prototype, fill levels are simulated via a background IoT loop that updates 20% of collection points every 30 seconds — demonstrating the real-time data pipeline. In production, this feed is replaced by actual sensor hardware. Sensor-based smart bins are already deployed commercially in Indian cities including Pune and Indore, as well as internationally by companies like Bigbelly and Sensoneo.

### 4. AI-Optimised Route Planning
CycleIQ uses **Google OR-Tools** with a GlobalSpanCostCoefficient constraint to generate balanced truck routes based on live fill data. Trucks are only dispatched to bins that are above a fill threshold, and routes are distributed evenly across the truck fleet to prevent any single truck being overloaded.

This replaces fixed-schedule collection — a major source of inefficiency — with demand-driven collection. The system visualises routes on an interactive map with per-truck details including estimated distance and number of stops.

### 5. 7-Day Waste Volume Forecasting
Using **Facebook Prophet** (with a statistical fallback for environments where Prophet is unavailable), CycleIQ forecasts waste volume for each of Delhi's 20 wards over the next 7 days. Each ward has a distinct forecast based on its historical volume, seasonality, and day-of-week patterns.

This allows city planners to pre-position trucks and staff before high-volume periods (festivals, weekends, seasonal spikes) rather than reacting after bins overflow.

### 6. Circular Economy Tracking
CycleIQ quantifies the environmental impact of the system in real time:
- **Recycling diversion rate** — what percentage of waste is being recovered instead of landfilled
- **Composting potential** — organic waste available for composting
- **CO₂ savings** — calculated against a full-landfill baseline
- **Material flow Sankey diagram** — visualises where each tonne of waste goes

### 7. AI Chat for City Officials
A natural language interface powered by **Groq / Llama 3.1** allows city officials to query the system in plain English: *"Which ward has the highest hazardous waste concentration?"* or *"Which bins need urgent collection today?"* The LLM responds using real data from the database, not generic answers.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI + PostgreSQL (Neon) |
| ORM | SQLAlchemy |
| Computer Vision | YOLOv8n (Ultralytics) |
| Forecasting | Facebook Prophet + statistical fallback |
| Route Optimization | Google OR-Tools |
| LLM | Groq API / Llama 3.1 8B Instant |
| Frontend | Streamlit |
| Maps | Folium + streamlit-folium |
| Charts | Plotly |
| Live Camera | streamlit-webrtc + aiortc |

---

## Project Structure

```
cycleiq/
├── main.py                          # FastAPI app + IoT simulation loop
├── database.py                      # Neon PostgreSQL connection
├── .env                             # Credentials (not committed)
├── .env.example                     # Template for setup
├── requirements.txt
├── models/
│   ├── waste_model.py               # CollectionPoint, WasteClassification
│   ├── forecast_model.py            # WasteForecast, WasteHistory
│   └── citizen_model.py             # Citizen, CitizenActivity, OptimizedRoute
├── routers/
│   ├── waste_router.py              # CV classify, collection points, ward summary
│   ├── forecast_router.py           # 7-day forecasts, history
│   ├── routes_router.py             # OR-Tools route optimization
│   ├── dashboard_router.py          # KPIs + LLM query
│   └── citizens_router.py           # Leaderboard, register, activity
├── ml/
│   ├── cv_module.py                 # YOLOv8 + image-aware fallback
│   ├── forecasting.py               # Prophet + statistical fallback
│   ├── route_optimizer.py           # OR-Tools balanced routing
│   └── llm_engine.py                # Groq/Llama with real DB context
├── data/
│   └── synthetic_data.py            # 20 Delhi wards, 180 days history, 150 citizens
└── streamlit_app/
    ├── app.py                       # Main dashboard — 6 KPIs, alerts
    └── pages/
        ├── 1_waste_map.py           # Folium map + ward composition
        ├── 2_forecasting.py         # Prophet 7-day forecast per ward
        ├── 3_routes.py              # OR-Tools map + truck cards
        ├── 4_llm_chat.py            # AI chat with real data context
        ├── 5_citizens.py            # Leaderboard + register
        ├── 6_cv_classify.py         # Live camera + image upload classifier
        └── 7_circular_economy.py    # Sankey + CO₂ impact + diversion rates
```

---

## Setup & Running

### Prerequisites
- Python 3.10+
- A Neon PostgreSQL database
- A Groq API key

### Installation

```bash
git clone https://github.com/RAK2315/CycleIQ-Waste-Intelligence-System.git
cd CycleIQ-Waste-Intelligence-System

pip install fastapi uvicorn sqlalchemy psycopg2-binary python-dotenv pydantic groq python-multipart
pip install streamlit plotly pandas numpy pillow httpx requests
pip install folium streamlit-folium
pip install ultralytics
pip install ortools
pip install streamlit-webrtc aiortc opencv-python-headless
```

### Environment Variables

Create a `.env` file in the root directory:

```
DATABASE_URL=your_neon_postgresql_connection_string
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.1-8b-instant
```

### Running

**Terminal 1 — API:**
```bash
uvicorn main:app --reload --port 8000
```

**Terminal 2 — Streamlit:**
```bash
cd streamlit_app
streamlit run app.py
```

The database seeds automatically on first startup with synthetic data for 20 Delhi wards, 150 citizens, and 180 days of waste history.

- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Dashboard: http://localhost:8501

---

## Pages

| Page | Purpose |
|---|---|
| Overview | 6 live KPIs, fill level alerts, recent activity |
| Waste Map | Interactive Folium map of all collection points colour-coded by fill level, ward composition chart |
| Forecasting | 7-day Prophet forecast per ward, historical trend, all-wards comparison |
| Route Optimizer | OR-Tools balanced truck routes on map, per-truck stats, estimated savings |
| AI Chat | Natural language queries against live database via Groq/Llama 3.1 |
| Citizen Portal | Leaderboard, tier system (Bronze → Platinum), register new citizens |
| CV Classifier | Live webcam stream with YOLOv8 bounding boxes, or image upload mode |
| Circular Economy | Material flow Sankey, ward diversion rates, 30-day CO₂ savings trend |

---

## Deployment Notes

The FastAPI backend runs locally and connects to a hosted Neon PostgreSQL database. The Streamlit frontend can be deployed to Streamlit Cloud (share.streamlit.io) pointing to `streamlit_app/app.py`. For the full system to work when hosted, the API also needs to be deployed publicly — Railway.app or Render.com work well for this.

For local demo (recommended for presentations), run both terminals and open `localhost:8501`.

---

## Team

**Team Sigmoid — JSS University**
- Rehaan Ahmad Khan
- Krishna Agarwaal  
- Daksh Kumar

**Event:** India Innovates 2026 — World's Largest Civic Tech Hackathon  
**Finale:** March 28, 2026 · Bharat Mandapam, New Delhi