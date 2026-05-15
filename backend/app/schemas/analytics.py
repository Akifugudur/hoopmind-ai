from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


# ---------- Shot Probability ----------
class ShotProbabilityRequest(BaseModel):
    shot_distance: float = Field(..., ge=0, le=94, description="Distance from basket in feet")
    shot_angle: float = Field(..., ge=-180, le=180)
    shot_type: str = Field(..., description="Jump Shot | Layup | Dunk | Hook Shot | Floater")
    is_three_pointer: bool = False
    is_catch_and_shoot: bool = False
    defender_distance: float = Field(default=4.0, ge=0, le=30)
    quarter: int = Field(default=2, ge=1, le=5)
    time_remaining_seconds: float = Field(default=300, ge=0)
    shot_clock: Optional[float] = Field(default=14.0, ge=0, le=24)
    is_home: bool = True
    dribbles_before_shot: int = Field(default=1, ge=0)
    touch_time: float = Field(default=2.0, ge=0)


class ShotProbabilityResponse(BaseModel):
    probability: float
    made_probability_pct: float
    shot_quality: str  # "Elite" | "Good" | "Average" | "Poor"
    expected_value: float  # points per shot
    model_used: str
    feature_importance: Optional[Dict[str, float]] = None
    comparable_player_avg: Optional[float] = None


# ---------- Player Similarity ----------
class PlayerSimilarityRequest(BaseModel):
    player_id: int
    top_n: int = Field(default=5, ge=1, le=20)


class SimilarPlayer(BaseModel):
    player_id: int
    player_name: str
    team_name: Optional[str]
    position: str
    similarity_score: float
    points_per_game: float
    assists_per_game: float
    rebounds_per_game: float
    player_efficiency_rating: float
    cluster: int


class PlayerSimilarityResponse(BaseModel):
    target_player: str
    target_player_id: int
    cluster: int
    similar_players: List[SimilarPlayer]
    pca_coordinates: Optional[List[Dict[str, Any]]] = None


# ---------- Player Performance Prediction ----------
class PlayerPerformanceRequest(BaseModel):
    player_id: int
    opponent_team_id: Optional[int] = None
    is_home: bool = True
    rest_days: int = Field(default=1, ge=0, le=10)
    projected_minutes: float = Field(default=32.0, ge=0, le=48)


class PlayerPerformanceResponse(BaseModel):
    player_id: int
    player_name: str
    predicted_points: float
    predicted_assists: float
    predicted_rebounds: float
    predicted_threes: float
    predicted_efficiency: float
    confidence_interval: Dict[str, float]
    matchup_difficulty: str  # "Easy" | "Average" | "Tough"


# ---------- Model Metrics ----------
class ModelMetrics(BaseModel):
    model_name: str
    accuracy: float
    roc_auc: float
    precision: float
    recall: float
    f1_score: float
    training_samples: int


class ModelMetricsResponse(BaseModel):
    shot_probability_models: List[ModelMetrics]
    best_model: str
    feature_importance: Dict[str, float]
    training_date: str


# ---------- Team Win Probability ----------
class WinProbabilityRequest(BaseModel):
    home_team_id: int
    away_team_id: int


class WinProbabilityResponse(BaseModel):
    home_team: str
    away_team: str
    home_win_probability: float
    away_win_probability: float
    key_factors: List[Dict[str, Any]]
