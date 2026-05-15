"""initial schema

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "teams",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("abbreviation", sa.String(10), nullable=False),
        sa.Column("city", sa.String(100), nullable=False),
        sa.Column("conference", sa.String(20), nullable=False),
        sa.Column("division", sa.String(30), nullable=False),
        sa.Column("wins", sa.Integer(), default=0),
        sa.Column("losses", sa.Integer(), default=0),
        sa.Column("offensive_rating", sa.Float(), default=0.0),
        sa.Column("defensive_rating", sa.Float(), default=0.0),
        sa.Column("pace", sa.Float(), default=0.0),
        sa.Column("net_rating", sa.Float(), default=0.0),
        sa.Column("true_shooting_pct", sa.Float(), default=0.0),
        sa.Column("three_point_rate", sa.Float(), default=0.0),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("abbreviation"),
    )
    op.create_index("ix_teams_id", "teams", ["id"])

    op.create_table(
        "players",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("team_id", sa.Integer(), sa.ForeignKey("teams.id"), nullable=True),
        sa.Column("position", sa.String(10), nullable=False),
        sa.Column("jersey_number", sa.Integer(), nullable=True),
        sa.Column("age", sa.Integer(), nullable=True),
        sa.Column("height_cm", sa.Float(), nullable=True),
        sa.Column("weight_kg", sa.Float(), nullable=True),
        sa.Column("games_played", sa.Integer(), default=0),
        sa.Column("minutes_per_game", sa.Float(), default=0.0),
        sa.Column("points_per_game", sa.Float(), default=0.0),
        sa.Column("assists_per_game", sa.Float(), default=0.0),
        sa.Column("rebounds_per_game", sa.Float(), default=0.0),
        sa.Column("steals_per_game", sa.Float(), default=0.0),
        sa.Column("blocks_per_game", sa.Float(), default=0.0),
        sa.Column("turnovers_per_game", sa.Float(), default=0.0),
        sa.Column("field_goal_pct", sa.Float(), default=0.0),
        sa.Column("three_point_pct", sa.Float(), default=0.0),
        sa.Column("free_throw_pct", sa.Float(), default=0.0),
        sa.Column("true_shooting_pct", sa.Float(), default=0.0),
        sa.Column("player_efficiency_rating", sa.Float(), default=0.0),
        sa.Column("usage_rate", sa.Float(), default=0.0),
        sa.Column("win_shares", sa.Float(), default=0.0),
        sa.Column("box_plus_minus", sa.Float(), default=0.0),
        sa.Column("value_over_replacement", sa.Float(), default=0.0),
        sa.Column("is_active", sa.Boolean(), default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_players_id", "players", ["id"])
    op.create_index("ix_players_name", "players", ["name"])

    op.create_table(
        "games",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("home_team_id", sa.Integer(), sa.ForeignKey("teams.id"), nullable=False),
        sa.Column("away_team_id", sa.Integer(), sa.ForeignKey("teams.id"), nullable=False),
        sa.Column("season", sa.String(10), nullable=False),
        sa.Column("game_date", sa.Date(), nullable=False),
        sa.Column("home_score", sa.Integer(), nullable=True),
        sa.Column("away_score", sa.Integer(), nullable=True),
        sa.Column("home_win", sa.Boolean(), nullable=True),
        sa.Column("home_offensive_rating", sa.Float(), nullable=True),
        sa.Column("home_defensive_rating", sa.Float(), nullable=True),
        sa.Column("away_offensive_rating", sa.Float(), nullable=True),
        sa.Column("away_defensive_rating", sa.Float(), nullable=True),
        sa.Column("pace", sa.Float(), nullable=True),
        sa.Column("home_win_probability", sa.Float(), nullable=True),
        sa.Column("away_win_probability", sa.Float(), nullable=True),
        sa.Column("is_finished", sa.Boolean(), default=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_games_season", "games", ["season"])
    op.create_index("ix_games_game_date", "games", ["game_date"])

    op.create_table(
        "shots",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("player_id", sa.Integer(), sa.ForeignKey("players.id"), nullable=False),
        sa.Column("game_id", sa.Integer(), sa.ForeignKey("games.id"), nullable=False),
        sa.Column("loc_x", sa.Float(), nullable=False),
        sa.Column("loc_y", sa.Float(), nullable=False),
        sa.Column("shot_distance", sa.Float(), nullable=False),
        sa.Column("shot_angle", sa.Float(), nullable=False),
        sa.Column("shot_type", sa.String(30), nullable=False),
        sa.Column("shot_zone", sa.String(30), nullable=False),
        sa.Column("action_type", sa.String(50), nullable=False),
        sa.Column("is_three_pointer", sa.Boolean(), default=False),
        sa.Column("is_catch_and_shoot", sa.Boolean(), default=False),
        sa.Column("quarter", sa.Integer(), nullable=False),
        sa.Column("time_remaining_seconds", sa.Float(), nullable=False),
        sa.Column("shot_clock", sa.Float(), nullable=True),
        sa.Column("defender_distance", sa.Float(), nullable=True),
        sa.Column("dribbles_before_shot", sa.Integer(), nullable=True),
        sa.Column("touch_time", sa.Float(), nullable=True),
        sa.Column("score_margin", sa.Integer(), nullable=True),
        sa.Column("is_home", sa.Boolean(), default=True),
        sa.Column("shot_made", sa.Boolean(), nullable=False),
        sa.Column("shot_value", sa.Integer(), nullable=False),
        sa.Column("predicted_probability", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_shots_player_id", "shots", ["player_id"])
    op.create_index("ix_shots_game_id", "shots", ["game_id"])
    op.create_index("ix_shots_shot_made", "shots", ["shot_made"])

    op.create_table(
        "advanced_stats",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("player_id", sa.Integer(), sa.ForeignKey("players.id"), nullable=False),
        sa.Column("season", sa.String(10), nullable=False),
        sa.Column("paint_fg_pct", sa.Float(), default=0.0),
        sa.Column("midrange_fg_pct", sa.Float(), default=0.0),
        sa.Column("corner_three_pct", sa.Float(), default=0.0),
        sa.Column("above_break_three_pct", sa.Float(), default=0.0),
        sa.Column("offensive_rating", sa.Float(), default=0.0),
        sa.Column("defensive_rating", sa.Float(), default=0.0),
        sa.Column("assist_to_turnover", sa.Float(), default=0.0),
        sa.Column("steal_pct", sa.Float(), default=0.0),
        sa.Column("block_pct", sa.Float(), default=0.0),
        sa.Column("rebound_pct", sa.Float(), default=0.0),
        sa.Column("three_point_attempt_rate", sa.Float(), default=0.0),
        sa.Column("free_throw_attempt_rate", sa.Float(), default=0.0),
        sa.Column("similarity_cluster", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_advanced_stats_player_id", "advanced_stats", ["player_id"])


def downgrade() -> None:
    op.drop_table("advanced_stats")
    op.drop_table("shots")
    op.drop_table("games")
    op.drop_table("players")
    op.drop_table("teams")
