from dataclasses import dataclass
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest

FEATURE_COLUMNS = [
    "value",
    "hour_of_day",
    "day_of_week",
    "rolling_mean_24h",
    "rolling_std_24h",
    "deviation_from_last_week",
]

DEFAULT_MODEL_PATH = Path(__file__).resolve().parents[2] / "data" / "isolation_forest.joblib"


@dataclass
class AnomalyResult:
    timestamp: pd.Timestamp
    region: str
    is_anomaly: bool
    severity_score: float
    contributing_features: dict[str, float]


class AnomalyDetector:
    def __init__(self, contamination: float = 0.02, random_state: int = 42):
        self.model = IsolationForest(contamination=contamination, random_state=random_state)
        self._fitted = False

    def fit(self, df: pd.DataFrame) -> None:
        """Train on engineered feature rows. Expects FEATURE_COLUMNS to be present."""
        X = self._prepare(df)
        self.model.fit(X)
        self._fitted = True

    def predict(self, df: pd.DataFrame) -> list[AnomalyResult]:
        """Score each row. Requires timestamp/region plus FEATURE_COLUMNS."""
        if not self._fitted:
            raise RuntimeError("Detector must be fit() before predict()")

        X = self._prepare(df)
        predictions = self.model.predict(X)  # -1 = anomaly, 1 = normal
        raw_scores = self.model.decision_function(X)  # higher = more normal

        results = []
        for i, (_, row) in enumerate(df.iterrows()):
            is_anomaly = predictions[i] == -1
            # decision_function is negative for anomalies; flip and clip to a
            # 0-1-ish severity score where higher means more anomalous.
            severity_score = max(0.0, -raw_scores[i])
            contributing_features = {col: float(row[col]) for col in FEATURE_COLUMNS}
            results.append(
                AnomalyResult(
                    timestamp=row["timestamp"],
                    region=row["region"],
                    is_anomaly=bool(is_anomaly),
                    severity_score=severity_score,
                    contributing_features=contributing_features,
                )
            )
        return results

    def save(self, path: Path = DEFAULT_MODEL_PATH) -> None:
        if not self._fitted:
            raise RuntimeError("Cannot save an unfitted detector")
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, path)

    def load(self, path: Path = DEFAULT_MODEL_PATH) -> None:
        self.model = joblib.load(path)
        self._fitted = True

    def _prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        missing = set(FEATURE_COLUMNS) - set(df.columns)
        if missing:
            raise ValueError(f"Missing required feature columns: {sorted(missing)}")
        return df[FEATURE_COLUMNS].fillna(0.0)
