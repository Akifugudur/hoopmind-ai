from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class AdvancedStats(Base):
    __tablename__ = "advanced_stats"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    season = Column(String(10), nullable=False)

    # Shooting zones
    paint_fg_pct = Column(Float, default=0.0)
    midrange_fg_pct = Column(Float, default=0.0)
    corner_three_pct = Column(Float, default=0.0)
    above_break_three_pct = Column(Float, default=0.0)

    # Advanced
    offensive_rating = Column(Float, default=0.0)
    defensive_rating = Column(Float, default=0.0)
    assist_to_turnover = Column(Float, default=0.0)
    steal_pct = Column(Float, default=0.0)
    block_pct = Column(Float, default=0.0)
    rebound_pct = Column(Float, default=0.0)
    three_point_attempt_rate = Column(Float, default=0.0)
    free_throw_attempt_rate = Column(Float, default=0.0)

    # Similarity cluster
    similarity_cluster = Column(Integer, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    player = relationship("Player", back_populates="advanced_stats")

    def __repr__(self):
        return f"<AdvancedStats player={self.player_id} season={self.season}>"
