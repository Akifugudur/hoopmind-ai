"""
Player Similarity Engine
K-Means clustering + Cosine similarity for finding similar NBA players.
"""
import numpy as np
import pandas as pd
import joblib
import os
import logging
from typing import List, Dict, Optional, Tuple
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

SIMILARITY_FEATURES = [
    "points_per_game",
    "assists_per_game",
    "rebounds_per_game",
    "steals_per_game",
    "blocks_per_game",
    "three_point_pct",
    "field_goal_pct",
    "free_throw_pct",
    "true_shooting_pct",
    "player_efficiency_rating",
    "usage_rate",
    "minutes_per_game",
    "turnovers_per_game",
    "box_plus_minus",
    "win_shares",
]

N_CLUSTERS = 6  # PG-type, Wing scorer, Stretch 4, Big, 3&D, Playmaker

CLUSTER_LABELS = {
    0: "Scoring Guard",
    1: "Playmaking Big",
    2: "3-and-D Wing",
    3: "Point Guard",
    4: "Interior Presence",
    5: "Versatile Forward",
}


class PlayerSimilarityEngine:
    def __init__(self, model_dir: str = "ml_models"):
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)

        self.kmeans: Optional[KMeans] = None
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=2)
        self.player_vectors: Optional[np.ndarray] = None
        self.player_df: Optional[pd.DataFrame] = None
        self.is_trained = False

    def train(self, player_df: pd.DataFrame) -> Dict:
        """
        Train K-Means clustering on player stats.
        player_df must have all SIMILARITY_FEATURES columns plus player metadata.
        """
        logger.info(f"Training player similarity on {len(player_df)} players...")

        df = player_df.copy()
        X = df[SIMILARITY_FEATURES].fillna(0).values

        # Scale
        X_scaled = self.scaler.fit_transform(X)
        self.player_vectors = X_scaled

        # K-Means
        self.kmeans = KMeans(
            n_clusters=N_CLUSTERS,
            init="k-means++",
            n_init=20,
            random_state=42,
        )
        clusters = self.kmeans.fit_predict(X_scaled)
        df["cluster"] = clusters

        # PCA for 2D visualization
        pca_coords = self.pca.fit_transform(X_scaled)
        df["pca_x"] = pca_coords[:, 0]
        df["pca_y"] = pca_coords[:, 1]
        df["cluster_label"] = df["cluster"].map(CLUSTER_LABELS)

        self.player_df = df

        logger.info(f"  Cluster distribution: {dict(zip(*np.unique(clusters, return_counts=True)))}")

        # Save
        self._save()
        self.is_trained = True

        return {
            "n_clusters": N_CLUSTERS,
            "cluster_distribution": {
                CLUSTER_LABELS.get(int(k), str(k)): int(v)
                for k, v in zip(*np.unique(clusters, return_counts=True))
            }
        }

    def find_similar(self, player_id: int, top_n: int = 5) -> Tuple[int, List[Dict]]:
        """Find top_n most similar players using cosine similarity."""
        if self.player_df is None:
            raise ValueError("Model not trained. Call train() or load() first.")

        # Find target player
        mask = self.player_df["id"] == player_id
        if not mask.any():
            raise ValueError(f"Player id={player_id} not found")

        target_idx = self.player_df[mask].index[0]
        target_vec = self.player_vectors[target_idx].reshape(1, -1)
        target_cluster = int(self.player_df.loc[target_idx, "cluster"])

        # Cosine similarity against all players
        sims = cosine_similarity(target_vec, self.player_vectors)[0]
        # Exclude self
        sims[target_idx] = -1

        top_indices = np.argsort(sims)[::-1][:top_n * 2]  # get more, filter later

        results = []
        for idx in top_indices:
            if len(results) >= top_n:
                break
            row = self.player_df.iloc[idx]
            results.append({
                "player_id": int(row["id"]),
                "player_name": str(row["name"]),
                "team_name": str(row.get("team_name", "")),
                "position": str(row["position"]),
                "similarity_score": round(float(sims[idx]), 4),
                "points_per_game": round(float(row["points_per_game"]), 1),
                "assists_per_game": round(float(row["assists_per_game"]), 1),
                "rebounds_per_game": round(float(row["rebounds_per_game"]), 1),
                "player_efficiency_rating": round(float(row["player_efficiency_rating"]), 1),
                "cluster": int(row["cluster"]),
            })

        return target_cluster, results

    def get_pca_data(self) -> List[Dict]:
        """Return PCA coordinates for all players (used for scatter plot)."""
        if self.player_df is None:
            return []
        return [
            {
                "id": int(row["id"]),
                "name": str(row["name"]),
                "x": round(float(row["pca_x"]), 4),
                "y": round(float(row["pca_y"]), 4),
                "cluster": int(row["cluster"]),
                "cluster_label": str(row["cluster_label"]),
                "position": str(row["position"]),
                "ppg": round(float(row["points_per_game"]), 1),
            }
            for _, row in self.player_df.iterrows()
        ]

    def _save(self):
        joblib.dump(self.kmeans, os.path.join(self.model_dir, "similarity_kmeans.pkl"))
        joblib.dump(self.scaler, os.path.join(self.model_dir, "similarity_scaler.pkl"))
        joblib.dump(self.pca, os.path.join(self.model_dir, "similarity_pca.pkl"))
        joblib.dump(self.player_vectors, os.path.join(self.model_dir, "player_vectors.pkl"))
        self.player_df.to_pickle(os.path.join(self.model_dir, "player_df.pkl"))
        logger.info(f"  Similarity engine saved to {self.model_dir}/")

    def load(self) -> bool:
        try:
            self.kmeans = joblib.load(os.path.join(self.model_dir, "similarity_kmeans.pkl"))
            self.scaler = joblib.load(os.path.join(self.model_dir, "similarity_scaler.pkl"))
            self.pca = joblib.load(os.path.join(self.model_dir, "similarity_pca.pkl"))
            self.player_vectors = joblib.load(os.path.join(self.model_dir, "player_vectors.pkl"))
            self.player_df = pd.read_pickle(os.path.join(self.model_dir, "player_df.pkl"))
            self.is_trained = True
            logger.info("Player similarity engine loaded.")
            return True
        except Exception as e:
            logger.warning(f"Could not load similarity model: {e}")
            return False


_sim_instance: Optional[PlayerSimilarityEngine] = None


def get_similarity_engine() -> PlayerSimilarityEngine:
    global _sim_instance
    if _sim_instance is None:
        _sim_instance = PlayerSimilarityEngine()
        _sim_instance.load()
    return _sim_instance
