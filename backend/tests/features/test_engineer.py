import pandas as pd
import pytest

from grid_agent.features.engineer import clean_and_resample, engineer_features


@pytest.fixture
def raw_hourly_df() -> pd.DataFrame:
    """48 hours of synthetic hourly demand for one region, with one gap hour
    removed to exercise clean_and_resample's interpolation."""
    timestamps = pd.date_range("2025-01-01", periods=48, freq="h", tz="UTC")
    values = [90000.0 + (i % 24) * 100 for i in range(48)]
    df = pd.DataFrame({"timestamp": timestamps, "region": "TEST", "value": values})
    return df.drop(index=10).reset_index(drop=True)  # drop one hour to create a gap


def test_clean_and_resample_fills_gap(raw_hourly_df):
    result = clean_and_resample(raw_hourly_df)

    assert len(result) == 48
    assert result["value"].isna().sum() == 0
    assert (result["timestamp"].diff().dropna() == pd.Timedelta(hours=1)).all()


def test_clean_and_resample_preserves_region(raw_hourly_df):
    result = clean_and_resample(raw_hourly_df)
    assert (result["region"] == "TEST").all()


def test_engineer_features_adds_expected_columns(raw_hourly_df):
    resampled = clean_and_resample(raw_hourly_df)
    result = engineer_features(resampled)

    expected_columns = {
        "hour_of_day",
        "day_of_week",
        "rolling_mean_24h",
        "rolling_std_24h",
        "deviation_from_last_week",
    }
    assert expected_columns.issubset(result.columns)


def test_engineer_features_hour_of_day_range(raw_hourly_df):
    resampled = clean_and_resample(raw_hourly_df)
    result = engineer_features(resampled)
    assert result["hour_of_day"].between(0, 23).all()


def test_engineer_features_deviation_from_last_week_is_nan_before_lag():
    # With fewer than 168 hours of history, deviation_from_last_week has no
    # same-hour-last-week value to compare against.
    timestamps = pd.date_range("2025-01-01", periods=48, freq="h", tz="UTC")
    df = pd.DataFrame({"timestamp": timestamps, "region": "TEST", "value": 90000.0})
    result = engineer_features(df)
    assert result["deviation_from_last_week"].isna().all()
