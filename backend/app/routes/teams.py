from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models import Team, Player
from app.schemas.team import TeamResponse, TeamList

router = APIRouter()


@router.get("/", response_model=TeamList)
def get_teams(
    page: int = Query(1, ge=1),
    page_size: int = Query(30, ge=1, le=60),
    conference: Optional[str] = Query(None, description="East | West"),
    sort_by: str = Query("wins", description="Sort field"),
    sort_desc: bool = Query(True),
    db: Session = Depends(get_db),
):
    query = db.query(Team)
    if conference:
        query = query.filter(Team.conference == conference.capitalize())

    total = query.count()
    sort_col = getattr(Team, sort_by, Team.wins)
    query = query.order_by(sort_col.desc() if sort_desc else sort_col.asc())
    teams = query.offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for t in teams:
        d = TeamResponse.model_validate(t)
        total_games = t.wins + t.losses
        d.win_pct = round(t.wins / total_games, 3) if total_games > 0 else 0.0
        items.append(d)

    return TeamList(items=items, total=total, page=page, page_size=page_size)


@router.get("/{team_id}", response_model=TeamResponse)
def get_team(team_id: int, db: Session = Depends(get_db)):
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail=f"Team {team_id} not found")
    result = TeamResponse.model_validate(team)
    total = team.wins + team.losses
    result.win_pct = round(team.wins / total, 3) if total > 0 else 0.0
    return result


@router.get("/{team_id}/roster")
def get_team_roster(team_id: int, db: Session = Depends(get_db)):
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    players = db.query(Player).filter(Player.team_id == team_id).order_by(
        Player.points_per_game.desc()
    ).all()

    return {
        "team_id": team_id,
        "team_name": team.name,
        "players": [
            {
                "id": p.id,
                "name": p.name,
                "position": p.position,
                "ppg": p.points_per_game,
                "apg": p.assists_per_game,
                "rpg": p.rebounds_per_game,
                "per": p.player_efficiency_rating,
                "ts_pct": p.true_shooting_pct,
            }
            for p in players
        ],
    }


@router.get("/{team_id}/stats-comparison")
def get_team_comparison(db: Session = Depends(get_db)):
    """Return all teams' key metrics for comparison chart."""
    teams = db.query(Team).order_by(Team.net_rating.desc()).all()
    return [
        {
            "id": t.id,
            "name": t.name,
            "abbreviation": t.abbreviation,
            "wins": t.wins,
            "losses": t.losses,
            "offensive_rating": t.offensive_rating,
            "defensive_rating": t.defensive_rating,
            "net_rating": t.net_rating,
            "pace": t.pace,
            "ts_pct": t.true_shooting_pct,
            "three_point_rate": t.three_point_rate,
        }
        for t in teams
    ]
