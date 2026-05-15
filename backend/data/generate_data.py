"""
NBA Synthetic Data Generator
Produces realistic NBA shot logs and player/team statistics.
Based on real NBA distributions from 2014-2024 seasons.
"""
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple
import random
import math

np.random.seed(42)
random.seed(42)

# ── Real NBA Teams ──────────────────────────────────────────────
NBA_TEAMS = [
    {"name": "Boston Celtics",        "abbreviation": "BOS", "city": "Boston",        "conference": "East", "division": "Atlantic"},
    {"name": "Brooklyn Nets",         "abbreviation": "BKN", "city": "Brooklyn",       "conference": "East", "division": "Atlantic"},
    {"name": "New York Knicks",       "abbreviation": "NYK", "city": "New York",       "conference": "East", "division": "Atlantic"},
    {"name": "Philadelphia 76ers",    "abbreviation": "PHI", "city": "Philadelphia",   "conference": "East", "division": "Atlantic"},
    {"name": "Toronto Raptors",       "abbreviation": "TOR", "city": "Toronto",        "conference": "East", "division": "Atlantic"},
    {"name": "Chicago Bulls",         "abbreviation": "CHI", "city": "Chicago",        "conference": "East", "division": "Central"},
    {"name": "Cleveland Cavaliers",   "abbreviation": "CLE", "city": "Cleveland",      "conference": "East", "division": "Central"},
    {"name": "Detroit Pistons",       "abbreviation": "DET", "city": "Detroit",        "conference": "East", "division": "Central"},
    {"name": "Indiana Pacers",        "abbreviation": "IND", "city": "Indianapolis",   "conference": "East", "division": "Central"},
    {"name": "Milwaukee Bucks",       "abbreviation": "MIL", "city": "Milwaukee",      "conference": "East", "division": "Central"},
    {"name": "Atlanta Hawks",         "abbreviation": "ATL", "city": "Atlanta",        "conference": "East", "division": "Southeast"},
    {"name": "Charlotte Hornets",     "abbreviation": "CHA", "city": "Charlotte",      "conference": "East", "division": "Southeast"},
    {"name": "Miami Heat",            "abbreviation": "MIA", "city": "Miami",          "conference": "East", "division": "Southeast"},
    {"name": "Orlando Magic",         "abbreviation": "ORL", "city": "Orlando",        "conference": "East", "division": "Southeast"},
    {"name": "Washington Wizards",    "abbreviation": "WAS", "city": "Washington",     "conference": "East", "division": "Southeast"},
    {"name": "Denver Nuggets",        "abbreviation": "DEN", "city": "Denver",         "conference": "West", "division": "Northwest"},
    {"name": "Minnesota Timberwolves","abbreviation": "MIN", "city": "Minneapolis",    "conference": "West", "division": "Northwest"},
    {"name": "Oklahoma City Thunder", "abbreviation": "OKC", "city": "Oklahoma City",  "conference": "West", "division": "Northwest"},
    {"name": "Portland Trail Blazers","abbreviation": "POR", "city": "Portland",       "conference": "West", "division": "Northwest"},
    {"name": "Utah Jazz",             "abbreviation": "UTA", "city": "Salt Lake City", "conference": "West", "division": "Northwest"},
    {"name": "Golden State Warriors", "abbreviation": "GSW", "city": "San Francisco",  "conference": "West", "division": "Pacific"},
    {"name": "LA Clippers",           "abbreviation": "LAC", "city": "Los Angeles",    "conference": "West", "division": "Pacific"},
    {"name": "Los Angeles Lakers",    "abbreviation": "LAL", "city": "Los Angeles",    "conference": "West", "division": "Pacific"},
    {"name": "Phoenix Suns",          "abbreviation": "PHX", "city": "Phoenix",        "conference": "West", "division": "Pacific"},
    {"name": "Sacramento Kings",      "abbreviation": "SAC", "city": "Sacramento",     "conference": "West", "division": "Pacific"},
    {"name": "Dallas Mavericks",      "abbreviation": "DAL", "city": "Dallas",         "conference": "West", "division": "Southwest"},
    {"name": "Houston Rockets",       "abbreviation": "HOU", "city": "Houston",        "conference": "West", "division": "Southwest"},
    {"name": "Memphis Grizzlies",     "abbreviation": "MEM", "city": "Memphis",        "conference": "West", "division": "Southwest"},
    {"name": "New Orleans Pelicans",  "abbreviation": "NOP", "city": "New Orleans",    "conference": "West", "division": "Southwest"},
    {"name": "San Antonio Spurs",     "abbreviation": "SAS", "city": "San Antonio",    "conference": "West", "division": "Southwest"},
]

# ── Real NBA Players (archetype-based with real names) ─────────
NBA_PLAYERS = [
    # Elite scorers
    {"name": "Jayson Tatum",      "position": "SF", "team": "BOS", "age": 26, "height": 203, "weight": 95,  "tier": "star"},
    {"name": "Jaylen Brown",      "position": "SG", "team": "BOS", "age": 27, "height": 196, "weight": 100, "tier": "star"},
    {"name": "Damian Lillard",    "position": "PG", "team": "MIL", "age": 34, "height": 188, "weight": 88,  "tier": "star"},
    {"name": "Giannis Antetokounmpo","position": "PF","team": "MIL","age": 29,"height": 211, "weight": 109, "tier": "superstar"},
    {"name": "Nikola Jokic",      "position": "C",  "team": "DEN", "age": 29, "height": 213, "weight": 129, "tier": "superstar"},
    {"name": "Jamal Murray",      "position": "PG", "team": "DEN", "age": 27, "height": 193, "weight": 95,  "tier": "star"},
    {"name": "Joel Embiid",       "position": "C",  "team": "PHI", "age": 30, "height": 213, "weight": 127, "tier": "superstar"},
    {"name": "Tyrese Maxey",      "position": "PG", "team": "PHI", "age": 23, "height": 188, "weight": 82,  "tier": "star"},
    {"name": "Stephen Curry",     "position": "PG", "team": "GSW", "age": 36, "height": 188, "weight": 84,  "tier": "superstar"},
    {"name": "Klay Thompson",     "position": "SG", "team": "DAL", "age": 34, "height": 198, "weight": 100, "tier": "star"},
    {"name": "Luka Doncic",       "position": "PG", "team": "DAL", "age": 25, "height": 201, "weight": 104, "tier": "superstar"},
    {"name": "Kyrie Irving",      "position": "PG", "team": "DAL", "age": 32, "height": 190, "weight": 88,  "tier": "star"},
    {"name": "LeBron James",      "position": "SF", "team": "LAL", "age": 39, "height": 206, "weight": 113, "tier": "superstar"},
    {"name": "Anthony Davis",     "position": "C",  "team": "LAL", "age": 31, "height": 208, "weight": 115, "tier": "star"},
    {"name": "Kevin Durant",      "position": "SF", "team": "PHX", "age": 35, "height": 208, "weight": 109, "tier": "superstar"},
    {"name": "Devin Booker",      "position": "SG", "team": "PHX", "age": 27, "height": 196, "weight": 97,  "tier": "star"},
    {"name": "Shai Gilgeous-Alexander","position":"PG","team":"OKC","age":26,"height": 198, "weight": 93,  "tier": "star"},
    {"name": "Chet Holmgren",     "position": "C",  "team": "OKC", "age": 22, "height": 216, "weight": 95,  "tier": "rising"},
    {"name": "Donovan Mitchell",  "position": "SG", "team": "CLE", "age": 27, "height": 185, "weight": 97,  "tier": "star"},
    {"name": "Darius Garland",    "position": "PG", "team": "CLE", "age": 24, "height": 185, "weight": 84,  "tier": "rising"},
    {"name": "Trae Young",        "position": "PG", "team": "ATL", "age": 26, "height": 185, "weight": 74,  "tier": "star"},
    {"name": "Dejounte Murray",   "position": "PG", "team": "NOP", "age": 27, "height": 193, "weight": 93,  "tier": "rising"},
    {"name": "Zion Williamson",   "position": "PF", "team": "NOP", "age": 23, "height": 198, "weight": 130, "tier": "star"},
    {"name": "Brandon Ingram",    "position": "SF", "team": "NOP", "age": 27, "height": 203, "weight": 91,  "tier": "star"},
    {"name": "Ja Morant",         "position": "PG", "team": "MEM", "age": 24, "height": 185, "weight": 80,  "tier": "star"},
    {"name": "Desmond Bane",      "position": "SG", "team": "MEM", "age": 26, "height": 196, "weight": 93,  "tier": "rising"},
    {"name": "Bam Adebayo",       "position": "C",  "team": "MIA", "age": 27, "height": 206, "weight": 116, "tier": "star"},
    {"name": "Jimmy Butler",      "position": "SF", "team": "MIA", "age": 35, "height": 201, "weight": 104, "tier": "star"},
    {"name": "Pascal Siakam",     "position": "PF", "team": "IND", "age": 30, "height": 206, "weight": 104, "tier": "star"},
    {"name": "Tyrese Haliburton",  "position": "PG","team": "IND", "age": 24, "height": 196, "weight": 84,  "tier": "star"},
    # Role players
    {"name": "Al Horford",        "position": "C",  "team": "BOS", "age": 38, "height": 206, "weight": 109, "tier": "role"},
    {"name": "Jrue Holiday",      "position": "PG", "team": "BOS", "age": 34, "height": 196, "weight": 97,  "tier": "role"},
    {"name": "Brook Lopez",       "position": "C",  "team": "MIL", "age": 36, "height": 213, "weight": 120, "tier": "role"},
    {"name": "Khris Middleton",   "position": "SF", "team": "MIL", "age": 33, "height": 201, "weight": 100, "tier": "role"},
    {"name": "Aaron Gordon",      "position": "PF", "team": "DEN", "age": 28, "height": 203, "weight": 100, "tier": "role"},
    {"name": "Michael Porter Jr.","position": "SF", "team": "DEN", "age": 26, "height": 206, "weight": 104, "tier": "role"},
    {"name": "Tobias Harris",     "position": "PF", "team": "PHI", "age": 32, "height": 206, "weight": 104, "tier": "role"},
    {"name": "Draymond Green",    "position": "PF", "team": "GSW", "age": 34, "height": 198, "weight": 104, "tier": "role"},
    {"name": "Maxi Kleber",       "position": "PF", "team": "DAL", "age": 33, "height": 208, "weight": 109, "tier": "role"},
    {"name": "Spencer Dinwiddie", "position": "PG", "team": "BKN", "age": 31, "height": 196, "weight": 97,  "tier": "role"},
]

SHOT_TYPES = ["Jump Shot", "Layup", "Dunk", "Hook Shot", "Floater", "Pull-Up Jump Shot", "Step Back Jump Shot", "Turnaround Jump Shot"]
SHOT_ZONES = ["Paint", "Mid-Range", "Left Corner 3", "Right Corner 3", "Above Break 3", "Backcourt"]
ACTION_TYPES = ["Jump Shot", "Driving Layup", "Cutting Layup", "Dunk", "Hook Shot", "Floater", "Pull-Up 3", "Catch and Shoot 3", "Step Back 3"]


def get_tier_stats(tier: str, position: str) -> Dict:
    """Generate realistic per-game stats based on player tier and position."""
    base = {
        "superstar": {"pts": (27, 6), "ast": (6, 2.5), "reb": (7, 2.5), "mpg": (34, 3),
                      "fg": (0.52, 0.04), "3p": (0.37, 0.04), "ft": (0.84, 0.05),
                      "per": (27, 4), "usg": (32, 4), "ws": (12, 3), "bpm": (7, 2), "vorp": (5, 1)},
        "star":      {"pts": (20, 5), "ast": (4, 2),   "reb": (5, 2),   "mpg": (32, 3),
                      "fg": (0.48, 0.04), "3p": (0.36, 0.05), "ft": (0.82, 0.06),
                      "per": (20, 3), "usg": (26, 4), "ws": (7,  2), "bpm": (3, 2), "vorp": (3, 1)},
        "rising":    {"pts": (17, 4), "ast": (4, 2),   "reb": (5, 2),   "mpg": (30, 3),
                      "fg": (0.47, 0.04), "3p": (0.35, 0.05), "ft": (0.80, 0.07),
                      "per": (18, 3), "usg": (24, 3), "ws": (5,  2), "bpm": (2, 2), "vorp": (2, 1)},
        "role":      {"pts": (11, 4), "ast": (3, 1.5), "reb": (4, 2),   "mpg": (26, 4),
                      "fg": (0.45, 0.04), "3p": (0.35, 0.06), "ft": (0.78, 0.08),
                      "per": (13, 3), "usg": (18, 4), "ws": (3,  2), "bpm": (0, 2), "vorp": (1, 1)},
    }
    s = base.get(tier, base["role"])

    # Position adjustments
    pos_adj = {
        "PG": {"ast": 2.0, "reb": -1.5},
        "SG": {"ast": 0.5},
        "SF": {},
        "PF": {"reb": 1.5, "ast": -1.0},
        "C":  {"reb": 3.0, "ast": -1.5, "pts": -2},
    }
    adj = pos_adj.get(position, {})

    def sample(key): return max(0, np.random.normal(s[key][0] + adj.get(key, 0), s[key][1]))

    pts = sample("pts")
    return {
        "games_played": int(np.random.normal(65, 10)),
        "minutes_per_game": round(sample("mpg"), 1),
        "points_per_game": round(pts, 1),
        "assists_per_game": round(sample("ast"), 1),
        "rebounds_per_game": round(sample("reb"), 1),
        "steals_per_game": round(max(0, np.random.normal(1.2, 0.5)), 1),
        "blocks_per_game": round(max(0, np.random.normal(0.8, 0.5)), 1),
        "turnovers_per_game": round(max(0.5, np.random.normal(2.0, 0.7)), 1),
        "field_goal_pct": round(min(0.70, max(0.30, np.random.normal(s["fg"][0], s["fg"][1]))), 3),
        "three_point_pct": round(min(0.55, max(0.20, np.random.normal(s["3p"][0], s["3p"][1]))), 3),
        "free_throw_pct": round(min(0.98, max(0.50, np.random.normal(s["ft"][0], s["ft"][1]))), 3),
        "true_shooting_pct": round(min(0.75, max(0.45, np.random.normal(s["fg"][0] + 0.05, 0.04))), 3),
        "player_efficiency_rating": round(max(5, sample("per")), 1),
        "usage_rate": round(max(10, min(40, sample("usg"))), 1),
        "win_shares": round(max(0, sample("ws")), 1),
        "box_plus_minus": round(np.random.normal(s["bpm"][0], s["bpm"][1]), 1),
        "value_over_replacement": round(max(0, sample("vorp")), 1),
    }


def generate_teams() -> List[Dict]:
    teams = []
    for t in NBA_TEAMS:
        wins = int(np.random.normal(41, 12))
        wins = max(15, min(65, wins))
        losses = 82 - wins
        off_rtg = round(np.random.normal(113.5, 3.5), 1)
        def_rtg = round(np.random.normal(113.0, 3.5), 1)
        teams.append({
            **t,
            "wins": wins,
            "losses": losses,
            "offensive_rating": off_rtg,
            "defensive_rating": def_rtg,
            "pace": round(np.random.normal(99.5, 2.5), 1),
            "net_rating": round(off_rtg - def_rtg, 1),
            "true_shooting_pct": round(np.random.normal(0.572, 0.015), 3),
            "three_point_rate": round(np.random.normal(0.40, 0.05), 3),
        })
    return teams


def generate_players(team_map: Dict[str, int]) -> List[Dict]:
    players = []
    for p in NBA_PLAYERS:
        stats = get_tier_stats(p["tier"], p["position"])
        players.append({
            "name": p["name"],
            "team_id": team_map.get(p["team"]),
            "position": p["position"],
            "jersey_number": random.randint(0, 55),
            "age": p["age"],
            "height_cm": float(p["height"]),
            "weight_kg": float(p["weight"]),
            "is_active": True,
            **stats,
        })
    return players


def _shot_probability(distance: float, angle: float, shot_type: str,
                       defender_dist: float, is_three: bool,
                       catch_and_shoot: bool, dribbles: int,
                       quarter: int, shot_clock: float,
                       player_fg_pct: float) -> float:
    """Physics-inspired shot probability model."""
    # Base probability from distance (exponential decay)
    if shot_type in ["Layup", "Dunk"]:
        base = 0.62 - distance * 0.015
    elif shot_type == "Floater":
        base = 0.48 - distance * 0.012
    else:
        # Jump shot probability: drops sharply beyond ~15ft, then levels for 3s
        if distance <= 5:
            base = 0.60
        elif distance <= 15:
            base = 0.60 - (distance - 5) * 0.025
        elif distance <= 22:
            base = 0.35 - (distance - 15) * 0.012
        else:
            base = 0.36 - (distance - 22) * 0.004  # 3-point range levels off

    # Angle penalty (corner threes slightly better)
    angle_rad = abs(angle) * math.pi / 180
    angle_factor = 1.0 - 0.08 * abs(math.sin(angle_rad))

    # Defender distance (tight defense hurts ~12%)
    if defender_dist < 2:
        def_factor = 0.78
    elif defender_dist < 4:
        def_factor = 0.88
    elif defender_dist < 6:
        def_factor = 0.96
    else:
        def_factor = 1.02

    # Catch and shoot bonus (+5% on jumpers)
    cas_factor = 1.05 if catch_and_shoot and shot_type not in ["Layup", "Dunk"] else 1.0

    # Dribble fatigue
    dribble_factor = max(0.88, 1.0 - dribbles * 0.015)

    # Shot clock pressure
    if shot_clock is not None and shot_clock < 4:
        clock_factor = 0.82
    elif shot_clock is not None and shot_clock < 8:
        clock_factor = 0.92
    else:
        clock_factor = 1.0

    # 4th quarter slight pressure drop
    quarter_factor = 0.96 if quarter == 4 else 1.0

    # Player skill adjustment
    skill_factor = (player_fg_pct - 0.46) * 1.5 + 1.0

    prob = base * angle_factor * def_factor * cas_factor * dribble_factor * clock_factor * quarter_factor * skill_factor
    return min(0.92, max(0.04, prob))


def generate_shots(players: List[Dict], player_ids: List[int],
                   game_ids: List[int], n_shots: int = 50000) -> pd.DataFrame:
    """Generate realistic NBA shot log data."""
    records = []
    shots_per_player = max(1, n_shots // len(players))

    for i, (player, pid) in enumerate(zip(players, player_ids)):
        fg_pct = player["field_goal_pct"]
        mpg = player["minutes_per_game"]
        usage = player["usage_rate"]
        # Estimate shot attempts per game
        fga_per_game = (usage / 100) * mpg * 0.85
        n_player_shots = int(shots_per_player * (usage / 20))

        for _ in range(n_player_shots):
            # Choose game
            game_id = random.choice(game_ids)
            quarter = np.random.choice([1, 2, 3, 4], p=[0.255, 0.255, 0.255, 0.235])
            time_rem = np.random.uniform(0, 720)
            shot_clock = np.random.uniform(1, 24) if np.random.random() > 0.05 else None

            # Shot selection: layup/dunk near basket, jumpers elsewhere
            r = np.random.random()
            if r < 0.28:  # At rim / paint
                shot_type = np.random.choice(["Layup", "Dunk", "Floater"], p=[0.55, 0.30, 0.15])
                distance = np.random.exponential(3.5)
                distance = min(distance, 6)
                angle = np.random.uniform(-60, 60)
                is_three = False
                zone = "Paint"
            elif r < 0.53:  # Mid-range
                shot_type = np.random.choice(["Jump Shot", "Pull-Up Jump Shot", "Turnaround Jump Shot"], p=[0.5, 0.35, 0.15])
                distance = np.random.uniform(10, 21)
                angle = np.random.uniform(-80, 80)
                is_three = False
                zone = "Mid-Range"
            else:  # 3-pointer
                # Corner 3 vs above-break 3
                corner = np.random.random() < 0.22
                if corner:
                    angle = np.random.choice([-1, 1]) * np.random.uniform(68, 90)
                    distance = np.random.uniform(22, 24)
                    zone = "Left Corner 3" if angle < 0 else "Right Corner 3"
                else:
                    angle = np.random.uniform(-65, 65)
                    distance = np.random.uniform(23, 30)
                    zone = "Above Break 3"
                shot_type = np.random.choice(["Jump Shot", "Pull-Up Jump Shot", "Step Back Jump Shot"], p=[0.55, 0.30, 0.15])
                is_three = True

            # Convert polar to court coords (basket at 0,5.25 ft from baseline)
            rad = angle * math.pi / 180
            loc_x = round(distance * math.sin(rad), 2)
            loc_y = round(distance * math.cos(rad) + 5.25, 2)

            # Context
            defender_dist = np.random.exponential(4.0) + 1.0
            catch_shoot = np.random.random() < 0.35 if is_three else np.random.random() < 0.15
            dribbles = 0 if catch_shoot else int(np.random.exponential(2))
            touch_time = np.random.uniform(0.5, 1.5) if catch_shoot else np.random.uniform(1.5, 5.0)
            is_home = np.random.random() < 0.5
            score_margin = int(np.random.normal(0, 12))

            # Shot probability
            prob = _shot_probability(
                distance, angle, shot_type, min(defender_dist, 20),
                is_three, catch_shoot, dribbles, quarter,
                shot_clock, fg_pct
            )
            shot_made = np.random.random() < prob
            action = "Catch and Shoot 3" if (catch_shoot and is_three) else shot_type

            records.append({
                "player_id": pid,
                "game_id": game_id,
                "loc_x": loc_x,
                "loc_y": loc_y,
                "shot_distance": round(distance, 2),
                "shot_angle": round(angle, 2),
                "shot_type": shot_type,
                "shot_zone": zone,
                "action_type": action,
                "is_three_pointer": is_three,
                "is_catch_and_shoot": catch_shoot,
                "quarter": int(quarter),
                "time_remaining_seconds": round(time_rem, 1),
                "shot_clock": round(shot_clock, 1) if shot_clock else None,
                "defender_distance": round(min(defender_dist, 20), 2),
                "dribbles_before_shot": dribbles,
                "touch_time": round(touch_time, 2),
                "score_margin": score_margin,
                "is_home": is_home,
                "shot_made": bool(shot_made),
                "shot_value": 3 if is_three else 2,
                "true_probability": round(prob, 4),  # for ML training label
            })

    df = pd.DataFrame(records)
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    return df


def generate_games(team_ids: List[int], n_games: int = 300) -> List[Dict]:
    """Generate game schedule with results."""
    import datetime
    games = []
    start_date = datetime.date(2023, 10, 24)
    teams = team_ids.copy()

    for i in range(n_games):
        home_id, away_id = random.sample(teams, 2)
        game_date = start_date + datetime.timedelta(days=random.randint(0, 150))
        home_off = round(np.random.normal(113.5, 4), 1)
        away_off = round(np.random.normal(113.5, 4), 1)
        home_def = round(np.random.normal(113.0, 4), 1)
        away_def = round(np.random.normal(113.0, 4), 1)

        # Home court ~60% win rate base, adjusted by ratings
        home_advantage = 0.06
        rating_diff = (home_off - home_def) - (away_off - away_def)
        home_win_prob = 0.5 + home_advantage + rating_diff * 0.02
        home_win_prob = min(0.90, max(0.10, home_win_prob))
        home_win = np.random.random() < home_win_prob

        home_score = int(np.random.normal(113, 9))
        if home_win:
            away_score = home_score - int(np.random.uniform(1, 20))
        else:
            away_score = home_score + int(np.random.uniform(1, 20))
        away_score = max(80, away_score)

        games.append({
            "home_team_id": home_id,
            "away_team_id": away_id,
            "season": "2023-24",
            "game_date": game_date,
            "home_score": home_score,
            "away_score": away_score,
            "home_win": bool(home_win),
            "home_offensive_rating": home_off,
            "home_defensive_rating": home_def,
            "away_offensive_rating": away_off,
            "away_defensive_rating": away_def,
            "pace": round(np.random.normal(99.5, 2.5), 1),
            "home_win_probability": round(home_win_prob, 3),
            "away_win_probability": round(1 - home_win_prob, 3),
            "is_finished": True,
        })
    return games


def generate_advanced_stats(player_ids: List[int], players: List[Dict]) -> List[Dict]:
    records = []
    for pid, player in zip(player_ids, players):
        fg = player["field_goal_pct"]
        records.append({
            "player_id": pid,
            "season": "2023-24",
            "paint_fg_pct": round(min(0.80, max(0.40, np.random.normal(0.62, 0.07))), 3),
            "midrange_fg_pct": round(min(0.60, max(0.30, np.random.normal(fg - 0.03, 0.05))), 3),
            "corner_three_pct": round(min(0.55, max(0.25, np.random.normal(0.40, 0.06))), 3),
            "above_break_three_pct": round(min(0.50, max(0.20, np.random.normal(0.36, 0.06))), 3),
            "offensive_rating": round(np.random.normal(112, 6), 1),
            "defensive_rating": round(np.random.normal(112, 6), 1),
            "assist_to_turnover": round(max(0.5, np.random.normal(2.5, 0.8)), 2),
            "steal_pct": round(max(0, np.random.normal(1.5, 0.5)), 2),
            "block_pct": round(max(0, np.random.normal(1.2, 0.7)), 2),
            "rebound_pct": round(max(2, np.random.normal(8, 3)), 2),
            "three_point_attempt_rate": round(np.random.uniform(0.15, 0.65), 3),
            "free_throw_attempt_rate": round(np.random.uniform(0.15, 0.55), 3),
            "similarity_cluster": None,
        })
    return records


if __name__ == "__main__":
    print("Generating teams...")
    teams = generate_teams()
    print(f"  {len(teams)} teams")

    print("Generating players...")
    team_map = {t["abbreviation"]: i + 1 for i, t in enumerate(teams)}
    players = generate_players(team_map)
    print(f"  {len(players)} players")

    print("Done. Use seed_db.py to load into PostgreSQL.")
