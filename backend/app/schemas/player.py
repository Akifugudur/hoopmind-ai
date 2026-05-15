from pydantic import BaseModel
from typing import Optional, List


class PlayerBase(BaseModel):
    name: str
    position: str
    team_id: Optional[int] = None
    jersey_number: Optional[int] = None
    age: Optional[int] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None


class PlayerCreate(PlayerBase):
    games_played: int = 0
    minutes_per_game: float = 0.0
    points_per_game: float = 0.0
    assists_per_game: float = 0.0
    rebounds_per_game: float = 0.0
    steals_per_game: float = 0.0
    blocks_per_game: float = 0.0
    turnovers_per_game: float = 0.0
    field_goal_pct: float = 0.0
    three_point_pct: float = 0.0
    free_throw_pct: float = 0.0
    true_shooting_pct: float = 0.0
    player_efficiency_rating: float = 0.0
    usage_rate: float = 0.0
    win_shares: float = 0.0
    box_plus_minus: float = 0.0
    value_over_replacement: float = 0.0


class PlayerResponse(PlayerBase):
    id: int
    games_played: int
    minutes_per_game: float
    points_per_game: float
    assists_per_game: float
    rebounds_per_game: float
    steals_per_game: float
    blocks_per_game: float
    turnovers_per_game: float
    field_goal_pct: float
    three_point_pct: float
    free_throw_pct: float
    true_shooting_pct: float
    player_efficiency_rating: float
    usage_rate: float
    win_shares: float
    box_plus_minus: float
    value_over_replacement: float
    is_active: bool
    team_name: Optional[str] = None

    model_config = {"from_attributes": True}


class PlayerList(BaseModel):
    items: List[PlayerResponse]
    total: int
    page: int
    page_size: int
