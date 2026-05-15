"""
Model Training Script
Run this after seeding the database to train all ML models.
Usage: python -m app.ml.train_models
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import logging
import pandas as pd
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Shot, Player, Team
from app.ml.shot_probability import ShotProbabilityModel
from app.ml.player_similarity import PlayerSimilarityEngine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s"
)
logger = logging.getLogger(__name__)

MODEL_DIR = os.environ.get("MODEL_DIR", "ml_models")


def load_shot_data(db: Session) -> pd.DataFrame:
    logger.info("Loading shot data from database...")
    shots = db.query(Shot).all()
    if not shots:
        raise ValueError("No shots in database. Run seed_db.py first.")
    records = [
        {
            "shot_distance": s.shot_distance,
            "shot_angle": s.shot_angle,
            "is_three_pointer": s.is_three_pointer,
            "is_catch_and_shoot": s.is_catch_and_shoot,
            "defender_distance": s.defender_distance,
            "quarter": s.quarter,
            "time_remaining_seconds": s.time_remaining_seconds,
            "shot_clock": s.shot_clock,
            "is_home": s.is_home,
            "dribbles_before_shot": s.dribbles_before_shot,
            "touch_time": s.touch_time,
            "score_margin": s.score_margin,
            "shot_type": s.shot_type,
            "shot_zone": s.shot_zone,
            "shot_made": s.shot_made,
        }
        for s in shots
    ]
    df = pd.DataFrame(records)
    logger.info(f"  Loaded {len(df):,} shots (make rate: {df['shot_made'].mean():.3f})")
    return df


def load_player_data(db: Session) -> pd.DataFrame:
    logger.info("Loading player data from database...")
    players = db.query(Player).join(Team, isouter=True).all()
    records = [
        {
            "id": p.id,
            "name": p.name,
            "position": p.position,
            "team_name": p.team.name if p.team else "Free Agent",
            "games_played": p.games_played,
            "minutes_per_game": p.minutes_per_game,
            "points_per_game": p.points_per_game,
            "assists_per_game": p.assists_per_game,
            "rebounds_per_game": p.rebounds_per_game,
            "steals_per_game": p.steals_per_game,
            "blocks_per_game": p.blocks_per_game,
            "turnovers_per_game": p.turnovers_per_game,
            "field_goal_pct": p.field_goal_pct,
            "three_point_pct": p.three_point_pct,
            "free_throw_pct": p.free_throw_pct,
            "true_shooting_pct": p.true_shooting_pct,
            "player_efficiency_rating": p.player_efficiency_rating,
            "usage_rate": p.usage_rate,
            "win_shares": p.win_shares,
            "box_plus_minus": p.box_plus_minus,
            "value_over_replacement": p.value_over_replacement,
        }
        for p in players
    ]
    df = pd.DataFrame(records)
    logger.info(f"  Loaded {len(df)} players")
    return df


def train_all():
    db = SessionLocal()
    try:
        # ── Shot Probability ──────────────────────────────────────
        logger.info("=" * 50)
        logger.info("TRAINING SHOT PROBABILITY MODELS")
        logger.info("=" * 50)
        shot_df = load_shot_data(db)
        shot_model = ShotProbabilityModel(model_dir=MODEL_DIR)
        metrics = shot_model.train(shot_df)

        logger.info("\nModel Comparison:")
        logger.info(f"{'Model':<25} {'Accuracy':>10} {'ROC-AUC':>10} {'F1':>10}")
        logger.info("-" * 55)
        for name, m in metrics.items():
            logger.info(f"{m['model_name']:<25} {m['accuracy']:>10.4f} {m['roc_auc']:>10.4f} {m['f1_score']:>10.4f}")
        logger.info(f"\n  ✓ Best model: {shot_model.best_model_name}")

        # ── Player Similarity ─────────────────────────────────────
        logger.info("=" * 50)
        logger.info("TRAINING PLAYER SIMILARITY ENGINE")
        logger.info("=" * 50)
        player_df = load_player_data(db)
        sim_engine = PlayerSimilarityEngine(model_dir=MODEL_DIR)
        sim_result = sim_engine.train(player_df)
        logger.info(f"  ✓ Clusters: {sim_result}")

        logger.info("\n✅ All models trained successfully!")

    except Exception as e:
        logger.error(f"Training failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    train_all()
