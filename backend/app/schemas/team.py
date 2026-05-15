from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class TeamBase(BaseModel):
    name: str
    abbreviation: str
    city: str
    conference: str
    division: str


class TeamCreate(TeamBase):
    wins: int = 0
    losses: int = 0
    offensive_rating: float = 0.0
    defensive_rating: float = 0.0
    pace: float = 0.0
    net_rating: float = 0.0
    true_shooting_pct: float = 0.0
    three_point_rate: float = 0.0


class TeamResponse(TeamBase):
    id: int
    wins: int
    losses: int
    offensive_rating: float
    defensive_rating: float
    pace: float
    net_rating: float
    true_shooting_pct: float
    three_point_rate: float
    win_pct: Optional[float] = None

    model_config = {"from_attributes": True}

    @property
    def win_pct(self) -> float:
        total = self.wins + self.losses
        return round(self.wins / total, 3) if total > 0 else 0.0


class TeamList(BaseModel):
    items: List[TeamResponse]
    total: int
    page: int
    page_size: int
