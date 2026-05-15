from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from app.database import get_db
from app.models import Player, Team
from app.schemas.player import PlayerResponse, PlayerList

router = APIRouter()


@router.get("/", response_model=PlayerList)
def get_players(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None, description="Search by name"),
    position: Optional[str] = Query(None, description="Filter by position"),
    team_id: Optional[int] = Query(None),
    sort_by: str = Query("points_per_game", description="Sort field"),
    sort_desc: bool = Query(True),
    db: Session = Depends(get_db),
):
    query = db.query(Player)

    if search:
        query = query.filter(Player.name.ilike(f"%{search}%"))
    if position:
        query = query.filter(Player.position == position.upper())
    if team_id:
        query = query.filter(Player.team_id == team_id)

    total = query.count()

    # Sorting
    sort_col = getattr(Player, sort_by, Player.points_per_game)
    query = query.order_by(sort_col.desc() if sort_desc else sort_col.asc())

    # Pagination
    players = query.offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for p in players:
        d = PlayerResponse.model_validate(p)
        d.team_name = p.team.name if p.team else None
        items.append(d)

    return PlayerList(items=items, total=total, page=page, page_size=page_size)


@router.get("/{player_id}", response_model=PlayerResponse)
def get_player(player_id: int, db: Session = Depends(get_db)):
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail=f"Player {player_id} not found")
    result = PlayerResponse.model_validate(player)
    result.team_name = player.team.name if player.team else None
    return result


@router.get("/{player_id}/shot-zones")
def get_player_shot_zones(player_id: int, db: Session = Depends(get_db)):
    """Return shooting percentages by zone for a specific player."""
    from app.models import Shot
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    from sqlalchemy import case
    zones = (
        db.query(
            Shot.shot_zone,
            func.count(Shot.id).label("attempts"),
            func.sum(case((Shot.shot_made == True, 1), else_=0)).label("made"),
            func.avg(Shot.shot_distance).label("avg_distance"),
        )
        .filter(Shot.player_id == player_id)
        .group_by(Shot.shot_zone)
        .all()
    )

    return {
        "player_id": player_id,
        "player_name": player.name,
        "zones": [
            {
                "zone": z.shot_zone,
                "attempts": z.attempts,
                "made": z.made,
                "fg_pct": round(z.made / z.attempts, 3) if z.attempts > 0 else 0.0,
                "avg_distance": round(float(z.avg_distance), 1) if z.avg_distance else 0.0,
            }
            for z in zones
        ],
    }


@router.get("/{player_id}/radar-stats")
def get_player_radar(player_id: int, db: Session = Depends(get_db)):
    """Return normalized radar chart stats for a player."""
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    # Normalize 0-100 against rough league maxes
    def norm(val, max_val):
        return round(min(100, (val / max_val) * 100), 1)

    return {
        "player_id": player_id,
        "player_name": player.name,
        "stats": [
            {"stat": "Scoring",    "value": norm(player.points_per_game, 35)},
            {"stat": "Playmaking", "value": norm(player.assists_per_game, 12)},
            {"stat": "Rebounding", "value": norm(player.rebounds_per_game, 14)},
            {"stat": "Defense",    "value": norm(player.steals_per_game + player.blocks_per_game, 4)},
            {"stat": "Efficiency", "value": norm(player.true_shooting_pct, 0.75)},
            {"stat": "Usage",      "value": norm(player.usage_rate, 40)},
        ],
    }
