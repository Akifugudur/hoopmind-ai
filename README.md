# 🏀 HoopMind AI — NBA Analytics Platform

> An advanced ML-powered NBA analytics platform combining shot probability prediction, player similarity clustering, and interactive visualizations.

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)](https://react.dev)
[![XGBoost](https://img.shields.io/badge/XGBoost-2.0-orange)](https://xgboost.readthedocs.io)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?logo=postgresql)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)](https://docker.com)
[![CI](https://img.shields.io/badge/CI-GitHub_Actions-2088FF?logo=github-actions)](/.github/workflows/ci.yml)

---

## Features

**Machine Learning**
- **Shot Make Probability** — XGBoost model trained on 60K+ shots with physics-inspired feature engineering. Outputs probability, shot quality rating, expected value, and SHAP-based feature importances.
- **Player Similarity Engine** — K-Means clustering (6 archetypes) + cosine similarity on 15 statistical features with PCA visualization.
- **Player Performance Prediction** — Contextual regression model using season averages, opponent defensive rating, home/away, rest days, and minutes projection.
- **Team Win Probability** — Logistic model using net rating differential and home court advantage.
- **Model Comparison** — Logistic Regression vs Random Forest vs XGBoost with Accuracy, ROC-AUC, Precision, Recall, F1 metrics.

**Backend (FastAPI)**
- RESTful API with OpenAPI docs at `/docs`
- Endpoints: `/players`, `/teams`, `/shots`, `/games`, `/analytics/*`
- Pagination, filtering, sorting on all collection endpoints
- Pydantic v2 validation, structured error handling

**Frontend (React)**
- Dark mode SaaS dashboard — single-page, tab-based
- NBA shot court visualization (SVG scatter plot)
- Interactive shot probability predictor
- Player radar charts, shot zone breakdowns
- Player cluster PCA scatter plot
- ML model performance comparison charts
- League leaderboards and standings

**Infrastructure**
- Docker Compose (postgres + backend + frontend)
- Alembic database migrations
- GitHub Actions CI pipeline (lint + test + Docker build)

---

## Architecture

```
hoopmind-ai/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entrypoint
│   │   ├── config.py            # Pydantic settings
│   │   ├── database.py          # SQLAlchemy engine & session
│   │   ├── models/              # ORM models (Team, Player, Game, Shot, AdvancedStats)
│   │   ├── schemas/             # Pydantic request/response schemas
│   │   ├── routes/              # API routers (players, teams, shots, games, analytics)
│   │   └── ml/
│   │       ├── shot_probability.py   # LR + RF + XGBoost training & inference
│   │       ├── player_similarity.py  # K-Means + cosine similarity engine
│   │       └── train_models.py       # Training script
│   ├── data/
│   │   ├── generate_data.py     # Realistic NBA data generator
│   │   └── seed_db.py           # DB population script
│   ├── alembic/                 # Database migrations
│   ├── tests/                   # pytest test suite
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── App.js               # Full single-page dashboard
│       ├── App.css              # Dark theme styles
│       └── services/api.js      # Axios API client
├── docker-compose.yml
├── .env.example
└── .github/workflows/ci.yml
```

---

## Quickstart

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running

### Run with Docker Compose (Recommended)

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/hoopmind-ai.git
cd hoopmind-ai

# 2. Copy environment file
cp .env.example .env

# 3. Start everything (postgres + backend + frontend)
docker compose up --build
```

On first start, Docker will automatically:
1. Start PostgreSQL
2. Run Alembic migrations
3. Seed the database with 30 NBA teams, 40 players, 300 games, 60K+ shots
4. Train all ML models (LR + RF + XGBoost + similarity engine)
5. Start the FastAPI server
6. Start the React frontend

| Service  | URL |
|----------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |

---

### Run Locally (Without Docker)

**Backend:**
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp ../.env.example .env
# Edit .env — set POSTGRES_HOST=localhost

# Run migrations
alembic upgrade head

# Seed database
python data/seed_db.py

# Train ML models
python -m app.ml.train_models

# Start API server
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm start
# Opens http://localhost:3000
```

---

## ML Models

### Shot Probability
Predicts the probability of a shot going in based on:

| Feature | Importance |
|---------|-----------|
| Shot Distance | ~28% |
| Defender Distance | ~18% |
| Shot Type (encoded) | ~14% |
| Distance × Defender interaction | ~11% |
| Shot Clock | ~8% |
| Catch & Shoot | ~6% |
| Quarter / Clutch Time | ~5% |
| ... | ... |

**Model Performance** (approximate, varies with random seed):

| Model | Accuracy | ROC-AUC | F1 |
|-------|----------|---------|-----|
| Logistic Regression | ~65% | ~0.70 | ~0.62 |
| Random Forest | ~66% | ~0.71 | ~0.63 |
| **XGBoost** | **~67%** | **~0.73** | **~0.64** |

### Player Similarity
6 player archetypes identified via K-Means:
- Scoring Guard
- Playmaking Big
- 3-and-D Wing
- Point Guard
- Interior Presence
- Versatile Forward

---

## API Reference

```
GET  /                                  # Health check
GET  /docs                              # OpenAPI interactive docs

GET  /players/                          # List players (paginated, filterable)
GET  /players/{id}                      # Player detail
GET  /players/{id}/radar-stats          # Radar chart data
GET  /players/{id}/shot-zones           # Shot zone breakdown

GET  /teams/                            # List teams
GET  /teams/{id}                        # Team detail
GET  /teams/{id}/roster                 # Team roster

GET  /shots/chart-data                  # Shot coordinates for court chart
GET  /shots/league-summary              # League FG% by zone

POST /analytics/shot-probability        # Predict shot make probability
POST /analytics/player-similarity       # Find similar players
POST /analytics/player-performance      # Predict player game stats
POST /analytics/win-probability         # Team win probability
GET  /analytics/model-metrics           # ML model performance metrics
GET  /analytics/leaderboard             # League leaderboards
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **API** | Python 3.11, FastAPI, Uvicorn |
| **ORM** | SQLAlchemy 2.0, Alembic |
| **Database** | PostgreSQL 15 |
| **Validation** | Pydantic v2 |
| **ML** | Scikit-learn, XGBoost, SHAP, Pandas, NumPy |
| **Frontend** | React 18, Recharts, Axios |
| **Infra** | Docker, Docker Compose |
| **CI/CD** | GitHub Actions |

---

## Development

```bash
# Run tests
cd backend && pytest tests/ -v

# Lint
flake8 app/ --max-line-length=120

# Retrain models
python -m app.ml.train_models

# Generate new migration
alembic revision --autogenerate -m "description"
```

---

## License

MIT — free to use for portfolio, learning, and personal projects.

---

*Built as a portfolio project demonstrating ML engineering, backend architecture, and data visualization skills.*
