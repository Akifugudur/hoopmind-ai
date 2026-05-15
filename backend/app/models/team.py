from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    abbreviation = Column(String(10), nullable=False, unique=True)
    city = Column(String(100), nullable=False)
    conference = Column(String(20), nullable=False)  # East / West
    division = Column(String(30), nullable=False)

    # Season stats
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    offensive_rating = Column(Float, default=0.0)
    defensive_rating = Column(Float, default=0.0)
    pace = Column(Float, default=0.0)
    net_rating = Column(Float, default=0.0)
    true_shooting_pct = Column(Float, default=0.0)
    three_point_rate = Column(Float, default=0.0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    players = relationship("Player", back_populates="team")
    home_games = relationship("Game", foreign_keys="Game.home_team_id", back_populates="home_team")
    away_games = relationship("Game", foreign_keys="Game.away_team_id", back_populates="away_team")

    def __repr__(self):
        return f"<Team {self.abbreviation}>"
