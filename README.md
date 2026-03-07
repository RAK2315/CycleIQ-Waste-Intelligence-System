# CycleIQ — Setup & Run Guide

## 1. Install dependencies

```bash
cd cycleiq
pip install -r requirements.txt
```

## 2. Run the FastAPI backend

Open Terminal 1:
```bash
cd cycleiq
uvicorn main:app --reload --port 8000
```

Wait until you see:
```
Database tables created successfully.
Database seeded successfully.
INFO: Application startup complete.
```

## 3. Run the Streamlit frontend

Open Terminal 2:
```bash
cd cycleiq/streamlit_app
streamlit run app.py
```

Your browser will open at http://localhost:8501

---

## Pages

| Page | URL | Description |
|------|-----|-------------|
| Overview | / | KPIs, fill levels, composition charts |
| Waste Map | /Waste_Map | Interactive Delhi map with collection points |
| Forecasting | /Forecasting | 7-day ward-wise waste predictions |
| Route Optimizer | /Routes | OR-Tools optimized truck routes |
| AI Assistant | /LLM_Chat | Chat with Llama 3.1 about your data |
| Citizens | /Citizens | Leaderboard and incentive tracker |

---

## API Docs

FastAPI auto-generates docs at:
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/redoc

---

## Troubleshooting

**YOLOv8 slow to load** — first run downloads the model (~6MB). Normal.

**Prophet install fails** — run: `pip install prophet --no-build-isolation`

**OR-Tools not available** — greedy routing fallback activates automatically.

**Neon connection timeout** — check your DATABASE_URL in .env is correct.
