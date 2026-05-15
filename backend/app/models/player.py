from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    position = Column(String(10), nullable=False)  # PG, SG, SF, PF, C
    jersey_number = Column(Integer, nullable=True)
    age = Column(Integer, nullable=True)
    height_cm = Column(Float, nullable=True)
    weight_kg = Column(Float, nullable=True)

    # Season averages
    games_played = Column(Integer, default=0)
    minutes_per_game = Column(Float, default=0.0)
    points_per_game = Column(Float, default=0.0)
    assists_per_game = Column(Float, default=0.0)
    rebounds_per_game = Column(Float, default=0.0)
    steals_per_game = Column(Float, default=0.0)
    blocks_per_game = Column(Float, default=0.0)
    turnovers_per_game = Column(Float, default=0.0)
    field_goal_pct = Column(Float, default=0.0)
    three_point_pct = Column(Float, default=0.0)
    free_throw_pct = Column(Float, default=0.0)
    true_shooting_pct = Column(Float, default=0.0)
    player_efficiency_rating = Column(Float, default=0.0)
    usage_rate = Column(Float, default=0.0)
    win_shares = Column(Float, default=0.0)
    box_plus_minus = Column(Float, default=0.0)
    value_over_replacement = Column(Float, default=0.0)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    team = relationship("Team", back_populates="players")
    shots = relationship("Shot", back_populates="player")
    advanced_stats = relationship("AdvancedStats", back_populates="player")

    def __repr__(self):
        return f"<Player {self.name}>"
