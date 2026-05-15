# HoopMind AI

NBA shot analytics and player similarity platform built with FastAPI, XGBoost, and React.

I built this to get hands-on experience with ML pipelines end-to-end — from data generation and feature engineering to model training, REST API, and a live dashboard. The shot probability model compares Logistic Regression, Random Forest, and XGBoost, and uses SHAP to explain predictions.

---

## What it does

- **Shot probability** — given shot distance, angle, defender distance, shot clock etc., predicts the likelihood of the shot going in
- **Player similarity** — clusters players by statistical profile using K-Means, finds similar players via cosine similarity
- **Player performance projection** — estimates per-game stats for a player based on matchup, rest days, home/away
- **Shot chart** — court visualization of made/missed shots
- **Model comparison** — accuracy, ROC-AUC, F1 across all three models

---

## Stack

- **Backend:** FastAPI, SQLAlchemy, PostgreSQL, Alembic
- **ML:** XGBoost, scikit-learn, SHAP, pandas
- **Frontend:** React, Recharts
- **Infra:** Docker Compose, GitHub Actions

---

## Running locally

You need Docker Desktop installed.

```bash
git clone https://github.com/Akifugudur/hoopmind-ai.git
cd hoopmind-ai
cp .env.example .env
docker compose up --build
```

First run takes a while — it seeds the DB with ~60K synthetic shots and trains all three models. After that:

- Frontend: http://localhost:3000
- API: http://localhost:8000
- Swagger docs: http://localhost:8000/docs

Subsequent runs are fast because Docker caches the layers.

---

## Project structure

```
backend/
  app/
    models/       # SQLAlchemy ORM (Team, Player, Game, Shot)
    schemas/      # Pydantic request/response models
    routes/       # API endpoints
    ml/           # Model training and inference
  data/           # Data generator + DB seeder
  alembic/        # Migrations

frontend/
  src/
    App.js        # Single-page dashboard
    services/     # API client
```

---

## Data

I used synthetic data generated to match real NBA shot distributions — distance decay, corner three bias, defender distance effects, shot clock pressure etc. are all modeled. Not real NBA data, but the distributions are realistic enough to train meaningful models on.

If you want to swap in real data, the seed script is in `backend/data/seed_db.py`.

---

## Model results

Approximate metrics on the test split (20%):

| Model | Accuracy | ROC-AUC | F1 |
|---|---|---|---|
| Logistic Regression | ~65% | ~0.70 | ~0.62 |
| Random Forest | ~66% | ~0.71 | ~0.63 |
| XGBoost | ~67% | ~0.73 | ~0.64 |

XGBoost wins but the gap is small. The biggest predictors are shot distance, defender distance, and their interaction term.

---

## API

```
GET  /players/                     list players, filterable + paginated
GET  /players/{id}/radar-stats     normalized skill ratings for radar chart
GET  /players/{id}/shot-zones      FG% breakdown by court zone

GET  /shots/chart-data             shot coordinates for court visualization
GET  /shots/league-summary         league-wide FG% by zone

POST /analytics/shot-probability   predict shot make probability
POST /analytics/player-similarity  find similar players
POST /analytics/player-performance project next-game stats
POST /analytics/win-probability    estimate team win probability
GET  /analytics/model-metrics      training metrics for all models
GET  /analytics/leaderboard        league stat leaders
```

---

## Notes

- No real NBA data — everything is synthetic but statistically grounded
- No auth, no Redis, no Celery — kept the scope focused
- Models are saved as `.pkl` files in a Docker volume so they persist across restarts
