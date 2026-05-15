from pydantic import BaseModel
from typing import Optional, List


class ShotBase(BaseModel):
    player_id: int
    game_id: int
    loc_x: float
    loc_y: float
    shot_distance: float
    shot_angle: float
    shot_type: str
    shot_zone: str
    action_type: str
    is_three_pointer: bool = False
    is_catch_and_shoot: bool = False
    quarter: int
    time_remaining_seconds: float
    shot_clock: Optional[float] = None
    defender_distance: Optional[float] = None
    dribbles_before_shot: Optional[int] = None
    touch_time: Optional[float] = None
    score_margin: Optional[int] = None
    is_home: bool = True
    shot_made: bool
    shot_value: int


class ShotCreate(ShotBase):
    pass


class ShotResponse(ShotBase):
    id: int
    predicted_probability: Optional[float] = None
    player_name: Optional[str] = None

    model_config = {"from_attributes": True}


class ShotList(BaseModel):
    items: List[ShotResponse]
    total: int
    page: int
    page_size: int


class ShotZoneSummary(BaseModel):
    zone: str
    attempts: int
    made: int
    fg_pct: float
    avg_distance: float
