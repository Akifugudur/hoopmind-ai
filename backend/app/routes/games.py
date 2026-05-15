from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Game, Team

router = APIRouter()


@router.get("/")
def get_games(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    season: str = Query("2023-24"),
    db: Session = Depends(get_db),
):
    query = db.query(Game).filter(Game.season == season).order_by(Game.game_date.desc())
    total = query.count()
    games = query.offset((page - 1) * page_size).limit(page_size).all()

    return {
        "items": [
            {
                "id": g.id,
                "home_team": g.home_team.name if g.home_team else "",
                "home_team_abbr": g.home_team.abbreviation if g.home_team else "",
                "away_team": g.away_team.name if g.away_team else "",
                "away_team_abbr": g.away_team.abbreviation if g.away_team else "",
                "game_date": str(g.game_date),
                "home_score": g.home_score,
                "away_score": g.away_score,
                "home_win": g.home_win,
                "home_win_probability": g.home_win_probability,
                "pace": g.pace,
            }
            for g in games
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }
