from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.models import Player, Team
from app.schemas.analytics import (
    ShotProbabilityRequest, ShotProbabilityResponse,
    PlayerSimilarityRequest, PlayerSimilarityResponse, SimilarPlayer,
    ModelMetricsResponse, ModelMetrics,
    PlayerPerformanceRequest, PlayerPerformanceResponse,
    WinProbabilityRequest, WinProbabilityResponse,
)
from app.ml.shot_probability import get_shot_model
from app.ml.player_similarity import get_similarity_engine, CLUSTER_LABELS

router = APIRouter()


# ── Shot Probability ──────────────────────────────────────────────
@router.post("/shot-probability", response_model=ShotProbabilityResponse)
def predict_shot_probability(req: ShotProbabilityRequest):
    """
    Predict the probability of a shot going in.
    Uses the best-performing trained model (XGBoost by default).
    """
    model = get_shot_model()
    if not model.is_trained:
        raise HTTPException(
            status_code=503,
            detail="ML models not yet trained. Please run: python -m app.ml.train_models"
        )

    features = {
        "shot_distance": req.shot_distance,
        "shot_angle": req.shot_angle,
        "is_three_pointer": req.is_three_pointer,
        "is_catch_and_shoot": req.is_catch_and_shoot,
        "defender_distance": req.defender_distance,
        "quarter": req.quarter,
        "time_remaining_seconds": req.time_remaining_seconds,
        "shot_clock": req.shot_clock,
        "is_home": req.is_home,
        "dribbles_before_shot": req.dribbles_before_shot,
        "touch_time": req.touch_time,
        "shot_type": req.shot_type,
        "shot_zone": _get_zone(req.shot_distance, req.shot_angle, req.is_three_pointer),
        "score_margin": 0,
    }

    prob, model_name = model.predict(features)
    shot_value = 3 if req.is_three_pointer else 2
    ev = prob * shot_value

    quality = (
        "Elite"   if prob >= 0.62 else
        "Good"    if prob >= 0.50 else
        "Average" if prob >= 0.40 else
        "Poor"
    )

    top_features = dict(list(model.feature_importance.items())[:8])

    return ShotProbabilityResponse(
        probability=round(prob, 4),
        made_probability_pct=round(prob * 100, 1),
        shot_quality=quality,
        expected_value=round(ev, 3),
        model_used=model_name,
        feature_importance=top_features,
        comparable_player_avg=0.466,  # ~league average FG%
    )


def _get_zone(distance: float, angle: float, is_three: bool) -> str:
    if distance <= 6:
        return "Paint"
    elif not is_three:
        return "Mid-Range"
    elif abs(angle) > 65:
        return "Left Corner 3" if angle < 0 else "Right Corner 3"
    else:
        return "Above Break 3"


# ── Player Similarity ──────────────────────────────────────────────
@router.post("/player-similarity", response_model=PlayerSimilarityResponse)
def get_player_similarity(req: PlayerSimilarityRequest, db: Session = Depends(get_db)):
    """Find players similar to a given player using K-Means + cosine similarity."""
    engine = get_similarity_engine()
    if not engine.is_trained:
        raise HTTPException(
            status_code=503,
            detail="Similarity model not trained. Run: python -m app.ml.train_models"
        )

    player = db.query(Player).filter(Player.id == req.player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail=f"Player {req.player_id} not found")

    try:
        cluster, similar = engine.find_similar(req.player_id, req.top_n)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    pca_data = engine.get_pca_data()

    return PlayerSimilarityResponse(
        target_player=player.name,
        target_player_id=player.id,
        cluster=cluster,
        similar_players=[SimilarPlayer(**s) for s in similar],
        pca_coordinates=pca_data[:50],  # limit for response size
    )


@router.get("/player-similarity/clusters")
def get_clusters():
    """Return all player cluster assignments for PCA visualization."""
    engine = get_similarity_engine()
    if not engine.is_trained:
        raise HTTPException(status_code=503, detail="Model not trained")
    return {"cluster_labels": CLUSTER_LABELS, "players": engine.get_pca_data()}


# ── Model Metrics ──────────────────────────────────────────────────
@router.get("/model-metrics", response_model=ModelMetricsResponse)
def get_model_metrics():
    """Return performance metrics for all trained shot probability models."""
    model = get_shot_model()
    if not model.is_trained:
        raise HTTPException(status_code=503, detail="Models not trained")

    model_list = [ModelMetrics(**m) for m in model.metrics.values()]

    return ModelMetricsResponse(
        shot_probability_models=model_list,
        best_model=model.best_model_name,
        feature_importance=model.feature_importance,
        training_date=datetime.now().strftime("%Y-%m-%d"),
    )


# ── Player Performance Prediction ─────────────────────────────────
@router.post("/player-performance", response_model=PlayerPerformanceResponse)
def predict_player_performance(req: PlayerPerformanceRequest, db: Session = Depends(get_db)):
    """
    Predict player performance for an upcoming game.
    Uses season averages + contextual adjustments.
    """
    player = db.query(Player).filter(Player.id == req.player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail=f"Player {req.player_id} not found")

    # Contextual multipliers
    home_factor = 1.03 if req.is_home else 0.97
    rest_factor = 1.0 + max(-0.05, min(0.04, (req.rest_days - 1) * 0.02))
    min_factor = req.projected_minutes / max(player.minutes_per_game, 1)

    # Opponent defensive rating adjustment
    def_factor = 1.0
    if req.opponent_team_id:
        opp = db.query(Team).filter(Team.id == req.opponent_team_id).first()
        if opp:
            # Lower opponent def_rating = better defense = harder to score
            league_avg_def = 113.0
            def_factor = 1.0 + (opp.defensive_rating - league_avg_def) * 0.008

    multiplier = home_factor * rest_factor * min_factor * def_factor

    import numpy as np
    noise = lambda: np.random.normal(1.0, 0.08)

    pred_pts = round(player.points_per_game * multiplier * noise(), 1)
    pred_ast = round(player.assists_per_game * multiplier * noise(), 1)
    pred_reb = round(player.rebounds_per_game * multiplier * noise(), 1)
    pred_3pm = round((player.points_per_game * 0.35 / 3) * player.three_point_pct * multiplier * noise(), 1)
    pred_eff = round(player.player_efficiency_rating * (multiplier ** 0.5) * noise(), 1)

    # Confidence intervals (~±15%)
    ci = {"lower": round(pred_pts * 0.75, 1), "upper": round(pred_pts * 1.25, 1)}

    difficulty = (
        "Tough"   if def_factor < 0.97 else
        "Average" if def_factor < 1.03 else
        "Easy"
    )

    return PlayerPerformanceResponse(
        player_id=player.id,
        player_name=player.name,
        predicted_points=max(0, pred_pts),
        predicted_assists=max(0, pred_ast),
        predicted_rebounds=max(0, pred_reb),
        predicted_threes=max(0, pred_3pm),
        predicted_efficiency=max(0, pred_eff),
        confidence_interval=ci,
        matchup_difficulty=difficulty,
    )


# ── Win Probability ────────────────────────────────────────────────
@router.post("/win-probability", response_model=WinProbabilityResponse)
def predict_win_probability(req: WinProbabilityRequest, db: Session = Depends(get_db)):
    home = db.query(Team).filter(Team.id == req.home_team_id).first()
    away = db.query(Team).filter(Team.id == req.away_team_id).first()
    if not home or not away:
        raise HTTPException(status_code=404, detail="One or both teams not found")

    import math
    # Logistic model: based on net rating differential + home advantage
    net_diff = home.net_rating - away.net_rating
    home_advantage = 3.2  # ~3 points home court advantage
    adjusted_diff = net_diff + home_advantage
    home_prob = 1 / (1 + math.exp(-adjusted_diff * 0.15))
    home_prob = min(0.92, max(0.08, home_prob))

    key_factors = [
        {"factor": "Home Court Advantage", "home_value": "+3.2 pts", "away_value": "—"},
        {"factor": "Net Rating",           "home_value": f"{home.net_rating:+.1f}", "away_value": f"{away.net_rating:+.1f}"},
        {"factor": "Offensive Rating",     "home_value": str(home.offensive_rating), "away_value": str(away.offensive_rating)},
        {"factor": "Defensive Rating",     "home_value": str(home.defensive_rating), "away_value": str(away.defensive_rating)},
        {"factor": "Season Record",        "home_value": f"{home.wins}-{home.losses}", "away_value": f"{away.wins}-{away.losses}"},
    ]

    return WinProbabilityResponse(
        home_team=home.name,
        away_team=away.name,
        home_win_probability=round(home_prob, 4),
        away_win_probability=round(1 - home_prob, 4),
        key_factors=key_factors,
    )


# ── League Leaderboard ─────────────────────────────────────────────
@router.get("/leaderboard")
def get_leaderboard(
    stat: str = "points_per_game",
    limit: int = 10,
    db: Session = Depends(get_db),
):
    valid_stats = [
        "points_per_game", "assists_per_game", "rebounds_per_game",
        "player_efficiency_rating", "true_shooting_pct", "win_shares",
        "box_plus_minus", "steals_per_game", "blocks_per_game",
    ]
    if stat not in valid_stats:
        raise HTTPException(status_code=400, detail=f"Invalid stat. Choose from: {valid_stats}")

    col = getattr(Player, stat)
    players = db.query(Player).order_by(col.desc()).limit(limit).all()

    return [
        {
            "rank": i + 1,
            "player_id": p.id,
            "player_name": p.name,
            "team": p.team.abbreviation if p.team else "FA",
            "position": p.position,
            "value": round(getattr(p, stat), 3),
            "stat": stat,
        }
        for i, p in enumerate(players)
    ]
