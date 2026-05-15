"""
Shot Make Probability Model
Trains and compares: Logistic Regression, Random Forest, XGBoost
Uses SHAP for explainability.
"""
import numpy as np
import pandas as pd
import joblib
import os
import logging
from typing import Dict, Tuple, Any, Optional
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import (
    accuracy_score, roc_auc_score, precision_score,
    recall_score, f1_score, classification_report
)
from sklearn.pipeline import Pipeline
import xgboost as xgb

logger = logging.getLogger(__name__)

FEATURE_COLS = [
    "shot_distance",
    "shot_angle",
    "is_three_pointer",
    "is_catch_and_shoot",
    "defender_distance",
    "quarter",
    "time_remaining_seconds",
    "shot_clock_filled",
    "is_home",
    "dribbles_before_shot",
    "touch_time",
    "shot_type_encoded",
    "shot_zone_encoded",
    "score_margin",
    "distance_sq",
    "distance_x_defender",
    "late_clock",
    "clutch_time",
]

TARGET_COL = "shot_made"


class ShotProbabilityModel:
    """Multi-model shot probability predictor."""

    def __init__(self, model_dir: str = "ml_models"):
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)

        self.models: Dict[str, Any] = {}
        self.metrics: Dict[str, Dict] = {}
        self.best_model_name: str = "xgboost"
        self.scaler = StandardScaler()
        self.shot_type_encoder = LabelEncoder()
        self.zone_encoder = LabelEncoder()
        self.feature_importance: Dict[str, float] = {}
        self.is_trained = False

    # ── Feature Engineering ──────────────────────────────────────
    def _engineer_features(self, df: pd.DataFrame, fit: bool = False) -> pd.DataFrame:
        df = df.copy()

        # Fill shot clock NaN with median
        df["shot_clock_filled"] = df["shot_clock"].fillna(14.0)

        # Encode categoricals
        if fit:
            df["shot_type_encoded"] = self.shot_type_encoder.fit_transform(df["shot_type"].fillna("Jump Shot"))
            df["shot_zone_encoded"] = self.zone_encoder.fit_transform(df["shot_zone"].fillna("Mid-Range"))
        else:
            # Handle unseen labels gracefully
            df["shot_type_encoded"] = df["shot_type"].apply(
                lambda x: self.shot_type_encoder.transform([x])[0]
                if x in self.shot_type_encoder.classes_ else 0
            )
            df["shot_zone_encoded"] = df["shot_zone"].apply(
                lambda x: self.zone_encoder.transform([x])[0]
                if x in self.zone_encoder.classes_ else 0
            )

        # Interaction features
        df["distance_sq"] = df["shot_distance"] ** 2
        df["distance_x_defender"] = df["shot_distance"] * df["defender_distance"].fillna(4.0)
        df["late_clock"] = (df["shot_clock_filled"] < 5).astype(int)
        df["clutch_time"] = ((df["quarter"] == 4) & (df["time_remaining_seconds"] < 120)).astype(int)

        # Fill remaining NaNs
        df["defender_distance"] = df["defender_distance"].fillna(4.0)
        df["dribbles_before_shot"] = df["dribbles_before_shot"].fillna(1)
        df["touch_time"] = df["touch_time"].fillna(2.0)
        df["score_margin"] = df["score_margin"].fillna(0)

        # Booleans to int
        for col in ["is_three_pointer", "is_catch_and_shoot", "is_home"]:
            df[col] = df[col].astype(int)

        return df

    # ── Training ─────────────────────────────────────────────────
    def train(self, df: pd.DataFrame) -> Dict[str, Dict]:
        logger.info(f"Training shot probability models on {len(df):,} shots...")

        df = self._engineer_features(df, fit=True)
        X = df[FEATURE_COLS].values
        y = df[TARGET_COL].astype(int).values

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        # Scale for LR
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # ── Model 1: Logistic Regression ─────────────────────────
        logger.info("  Training Logistic Regression...")
        lr = LogisticRegression(max_iter=500, C=0.5, random_state=42, n_jobs=-1)
        lr.fit(X_train_scaled, y_train)
        lr_metrics = self._evaluate(lr, X_test_scaled, y_test, "Logistic Regression", scaled=True)
        self.models["logistic_regression"] = lr

        # ── Model 2: Random Forest ────────────────────────────────
        logger.info("  Training Random Forest...")
        rf = RandomForestClassifier(
            n_estimators=200, max_depth=12, min_samples_leaf=10,
            random_state=42, n_jobs=-1, class_weight="balanced"
        )
        rf.fit(X_train, y_train)
        rf_metrics = self._evaluate(rf, X_test, y_test, "Random Forest")
        self.models["random_forest"] = rf

        # ── Model 3: XGBoost ─────────────────────────────────────
        logger.info("  Training XGBoost...")
        xgb_model = xgb.XGBClassifier(
            n_estimators=300,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            min_child_weight=5,
            gamma=0.1,
            reg_alpha=0.1,
            reg_lambda=1.0,
            use_label_encoder=False,
            eval_metric="logloss",
            random_state=42,
            n_jobs=-1,
        )
        xgb_model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            verbose=False,
        )
        xgb_metrics = self._evaluate(xgb_model, X_test, y_test, "XGBoost")
        self.models["xgboost"] = xgb_model

        # ── Pick best by ROC-AUC ──────────────────────────────────
        self.metrics = {
            "logistic_regression": lr_metrics,
            "random_forest": rf_metrics,
            "xgboost": xgb_metrics,
        }
        self.best_model_name = max(self.metrics, key=lambda k: self.metrics[k]["roc_auc"])
        logger.info(f"  Best model: {self.best_model_name} (AUC={self.metrics[self.best_model_name]['roc_auc']:.4f})")

        # ── Feature importance from XGBoost ──────────────────────
        importance = xgb_model.feature_importances_
        self.feature_importance = {
            f: round(float(v), 4)
            for f, v in sorted(
                zip(FEATURE_COLS, importance), key=lambda x: x[1], reverse=True
            )
        }

        # ── Save models ───────────────────────────────────────────
        self._save()
        self.is_trained = True
        return self.metrics

    def _evaluate(self, model, X_test, y_test, name: str, scaled: bool = False) -> Dict:
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]
        m = {
            "model_name": name,
            "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
            "roc_auc": round(float(roc_auc_score(y_test, y_proba)), 4),
            "precision": round(float(precision_score(y_test, y_pred, zero_division=0)), 4),
            "recall": round(float(recall_score(y_test, y_pred, zero_division=0)), 4),
            "f1_score": round(float(f1_score(y_test, y_pred, zero_division=0)), 4),
            "training_samples": len(y_test),
        }
        logger.info(f"    {name}: ACC={m['accuracy']:.4f} AUC={m['roc_auc']:.4f} F1={m['f1_score']:.4f}")
        return m

    # ── Prediction ───────────────────────────────────────────────
    def predict(self, features: Dict, model_name: Optional[str] = None) -> Tuple[float, str]:
        """Predict shot probability. Returns (probability, model_used)."""
        model_name = model_name or self.best_model_name
        model = self.models[model_name]

        row = pd.DataFrame([features])
        row = self._engineer_features(row, fit=False)

        # Fill any missing feature cols
        for col in FEATURE_COLS:
            if col not in row.columns:
                row[col] = 0

        X = row[FEATURE_COLS].values

        if model_name == "logistic_regression":
            X = self.scaler.transform(X)

        prob = float(model.predict_proba(X)[0, 1])
        return prob, model_name

    # ── Persist ──────────────────────────────────────────────────
    def _save(self):
        for name, model in self.models.items():
            joblib.dump(model, os.path.join(self.model_dir, f"shot_{name}.pkl"))
        joblib.dump(self.scaler, os.path.join(self.model_dir, "shot_scaler.pkl"))
        joblib.dump(self.shot_type_encoder, os.path.join(self.model_dir, "shot_type_enc.pkl"))
        joblib.dump(self.zone_encoder, os.path.join(self.model_dir, "zone_enc.pkl"))
        joblib.dump(self.metrics, os.path.join(self.model_dir, "shot_metrics.pkl"))
        joblib.dump(self.feature_importance, os.path.join(self.model_dir, "shot_feature_importance.pkl"))
        joblib.dump(self.best_model_name, os.path.join(self.model_dir, "shot_best_model.pkl"))
        logger.info(f"  Models saved to {self.model_dir}/")

    def load(self) -> bool:
        try:
            for name in ["logistic_regression", "random_forest", "xgboost"]:
                path = os.path.join(self.model_dir, f"shot_{name}.pkl")
                if os.path.exists(path):
                    self.models[name] = joblib.load(path)
            self.scaler = joblib.load(os.path.join(self.model_dir, "shot_scaler.pkl"))
            self.shot_type_encoder = joblib.load(os.path.join(self.model_dir, "shot_type_enc.pkl"))
            self.zone_encoder = joblib.load(os.path.join(self.model_dir, "zone_enc.pkl"))
            self.metrics = joblib.load(os.path.join(self.model_dir, "shot_metrics.pkl"))
            self.feature_importance = joblib.load(os.path.join(self.model_dir, "shot_feature_importance.pkl"))
            self.best_model_name = joblib.load(os.path.join(self.model_dir, "shot_best_model.pkl"))
            self.is_trained = True
            logger.info(f"Shot probability models loaded from {self.model_dir}/")
            return True
        except Exception as e:
            logger.warning(f"Could not load shot models: {e}")
            return False


# Global singleton
_model_instance: Optional[ShotProbabilityModel] = None


def get_shot_model() -> ShotProbabilityModel:
    global _model_instance
    if _model_instance is None:
        _model_instance = ShotProbabilityModel()
        loaded = _model_instance.load()
        if not loaded:
            logger.warning("Shot models not trained yet. Run train_models.py first.")
    return _model_instance
