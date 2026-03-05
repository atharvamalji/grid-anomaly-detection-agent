import pandas as pd
import pytest

from grid_agent.models.isolation_forest import AnomalyDetector, AnomalyResult


@pytest.fixture
def feature_df() -> pd.DataFrame:
    """200 hours of tightly-clustered synthetic 'normal' demand, plus one
    obvious outlier row so the detector has something real to flag."""
    n = 200
    timestamps = pd.date_range("2025-01-01", periods=n, freq="h", tz="UTC")
    rows = {
        "timestamp": timestamps,
        "region": ["TEST"] * n,
        "value": [90000.0 + (i % 5) * 50 for i in range(n)],
        "hour_of_day": [(i % 24) for i in range(n)],
        "day_of_week": [(i // 24) % 7 for i in range(n)],
        "rolling_mean_24h": [90000.0] * n,
        "rolling_std_24h": [200.0] * n,
        "deviation_from_last_week": [0.0] * n,
    }
    df = pd.DataFrame(rows)
    # Inject one extreme outlier hour: demand far above the normal cluster.
    df.loc[100, "value"] = 250000.0
    df.loc[100, "deviation_from_last_week"] = 150000.0
    return df


def test_fit_predict_roundtrip(feature_df):
    detector = AnomalyDetector(contamination=0.02)
    detector.fit(feature_df)
    results = detector.predict(feature_df)

    assert len(results) == len(feature_df)
    assert all(isinstance(r, AnomalyResult) for r in results)


def test_predict_flags_the_injected_outlier(feature_df):
    detector = AnomalyDetector(contamination=0.02)
    detector.fit(feature_df)
    results = detector.predict(feature_df)

    outlier_result = next(r for r in results if r.contributing_features["value"] == 250000.0)
    assert outlier_result.is_anomaly is True

    # The injected outlier should be at or near the top of the severity ranking.
    ranked = sorted(results, key=lambda r: r.severity_score, reverse=True)
    assert outlier_result in ranked[:3]


def test_predict_before_fit_raises(feature_df):
    detector = AnomalyDetector()
    with pytest.raises(RuntimeError):
        detector.predict(feature_df)


def test_predict_missing_feature_column_raises(feature_df):
    detector = AnomalyDetector()
    detector.fit(feature_df)
    with pytest.raises(ValueError):
        detector.predict(feature_df.drop(columns=["rolling_std_24h"]))
