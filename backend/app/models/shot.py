from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Shot(Base):
    __tablename__ = "shots"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False, index=True)

    # Shot location (NBA court coords: center = 0,0; basket at ~0,5.25)
    loc_x = Column(Float, nullable=False)   # feet from center
    loc_y = Column(Float, nullable=False)   # feet from baseline
    shot_distance = Column(Float, nullable=False)  # feet
    shot_angle = Column(Float, nullable=False)  # degrees

    # Shot type
    shot_type = Column(String(30), nullable=False)  # "Jump Shot", "Layup", etc.
    shot_zone = Column(String(30), nullable=False)   # "Paint", "Mid-Range", "3PT"
    action_type = Column(String(50), nullable=False)
    is_three_pointer = Column(Boolean, default=False)
    is_catch_and_shoot = Column(Boolean, default=False)

    # Context
    quarter = Column(Integer, nullable=False)  # 1-4, 5+ = OT
    time_remaining_seconds = Column(Float, nullable=False)
    shot_clock = Column(Float, nullable=True)
    defender_distance = Column(Float, nullable=True)  # feet
    dribbles_before_shot = Column(Integer, nullable=True)
    touch_time = Column(Float, nullable=True)  # seconds

    # Game state
    score_margin = Column(Integer, nullable=True)  # home - away at time of shot
    is_home = Column(Boolean, default=True)

    # Result
    shot_made = Column(Boolean, nullable=False, index=True)
    shot_value = Column(Integer, nullable=False)  # 2 or 3

    # ML prediction
    predicted_probability = Column(Float, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    player = relationship("Player", back_populates="shots")
    game = relationship("Game", back_populates="shots")

    def __repr__(self):
        return f"<Shot player={self.player_id} made={self.shot_made} dist={self.shot_distance:.1f}ft>"
