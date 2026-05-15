from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.routes import players, teams, shots, analytics, games

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"🏀 Starting {settings.app_name} v{settings.app_version}")
    yield
    logger.info("Shutting down HoopMind AI...")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
## HoopMind AI — NBA Analytics Platform

An advanced NBA analytics API powered by Machine Learning.

### Features
- 🎯 **Shot Probability** — Predict shot success probability with XGBoost
- 👤 **Player Similarity** — Find similar players using K-Means clustering & cosine similarity
- 📊 **Player Performance** — Predict game-level player stats
- 🏆 **Win Probability** — Team win probability estimation
- 📈 **Advanced Stats** — Comprehensive basketball analytics

### Models
- Logistic Regression
- Random Forest
- XGBoost (best performer)
""",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(players.router, prefix="/players", tags=["Players"])
app.include_router(teams.router, prefix="/teams", tags=["Teams"])
app.include_router(shots.router, prefix="/shots", tags=["Shots"])
app.include_router(games.router, prefix="/games", tags=["Games"])
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics & ML"])


@app.get("/", tags=["Health"])
async def root():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "operational",
        "docs": "/docs",
        "description": "NBA Analytics Platform powered by ML",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "environment": settings.environment}


@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(status_code=404, content={"detail": "Resource not found"})


@app.exception_handler(500)
async def server_error_handler(request, exc):
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
