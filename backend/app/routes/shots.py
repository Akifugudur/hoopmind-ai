from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from typing import Optional
from app.database import get_db
from app.models import Shot, Player
from app.schemas.shot import ShotResponse, ShotList

router = APIRouter()


@router.get("/", response_model=ShotList)
def get_shots(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    player_id: Optional[int] = Query(None),
    game_id: Optional[int] = Query(None),
    shot_zone: Optional[str] = Query(None),
    shot_made: Optional[bool] = Query(None),
    is_three: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(Shot)

    if player_id:
        query = query.filter(Shot.player_id == player_id)
    if game_id:
        query = query.filter(Shot.game_id == game_id)
    if shot_zone:
        query = query.filter(Shot.shot_zone == shot_zone)
    if shot_made is not None:
        query = query.filter(Shot.shot_made == shot_made)
    if is_three is not None:
        query = query.filter(Shot.is_three_pointer == is_three)

    total = query.count()
    shots = query.offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for s in shots:
        d = ShotResponse.model_validate(s)
        d.player_name = s.player.name if s.player else None
        items.append(d)

    return ShotList(items=items, total=total, page=page, page_size=page_size)


@router.get("/chart-data")
def get_shot_chart_data(
    player_id: Optional[int] = Query(None),
    limit: int = Query(500, ge=10, le=2000),
    db: Session = Depends(get_db),
):
    """Return shot coordinates for court visualization."""
    query = db.query(
        Shot.loc_x, Shot.loc_y, Shot.shot_made,
        Shot.shot_zone, Shot.shot_type,
        Shot.shot_distance, Shot.predicted_probability,
        Shot.is_three_pointer,
    )
    if player_id:
        query = query.filter(Shot.player_id == player_id)

    shots = query.order_by(func.random()).limit(limit).all()

    return [
        {
            "x": s.loc_x,
            "y": s.loc_y,
            "made": s.shot_made,
            "zone": s.shot_zone,
            "type": s.shot_type,
            "distance": round(s.shot_distance, 1),
            "prob": round(s.predicted_probability, 3) if s.predicted_probability else None,
            "three": s.is_three_pointer,
        }
        for s in shots
    ]


@router.get("/league-summary")
def get_league_shot_summary(db: Session = Depends(get_db)):
    """League-wide shooting summary by zone."""
    zones = (
        db.query(
            Shot.shot_zone,
            func.count(Shot.id).label("attempts"),
            func.sum(case((Shot.shot_made == True, 1), else_=0)).label("made"),
            func.avg(Shot.shot_distance).label("avg_distance"),
            func.avg(Shot.defender_distance).label("avg_defender_dist"),
        )
        .group_by(Shot.shot_zone)
        .all()
    )
    return [
        {
            "zone": z.shot_zone,
            "attempts": z.attempts,
            "made": z.made,
            "fg_pct": round(z.made / z.attempts, 3) if z.attempts > 0 else 0.0,
            "avg_distance": round(float(z.avg_distance), 1) if z.avg_distance else 0.0,
            "avg_defender_dist": round(float(z.avg_defender_dist), 1) if z.avg_defender_dist else 0.0,
        }
        for z in zones
    ]
