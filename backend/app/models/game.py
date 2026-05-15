from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    home_team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    away_team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    season = Column(String(10), nullable=False, index=True)  # e.g. "2023-24"
    game_date = Column(Date, nullable=False, index=True)

    # Scores
    home_score = Column(Integer, nullable=True)
    away_score = Column(Integer, nullable=True)
    home_win = Column(Boolean, nullable=True)

    # Game context
    home_offensive_rating = Column(Float, nullable=True)
    home_defensive_rating = Column(Float, nullable=True)
    away_offensive_rating = Column(Float, nullable=True)
    away_defensive_rating = Column(Float, nullable=True)
    pace = Column(Float, nullable=True)

    # Pregame win probabilities
    home_win_probability = Column(Float, nullable=True)
    away_win_probability = Column(Float, nullable=True)

    is_finished = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    home_team = relationship("Team", foreign_keys=[home_team_id], back_populates="home_games")
    away_team = relationship("Team", foreign_keys=[away_team_id], back_populates="away_games")
    shots = relationship("Shot", back_populates="game")

    def __repr__(self):
        return f"<Game {self.id}: {self.home_team_id} vs {self.away_team_id}>"
