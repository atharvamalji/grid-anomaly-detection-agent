import pandas as pd

ROLLING_WINDOW_HOURS = 24
SAME_HOUR_LAST_WEEK_LAG = 24 * 7


def clean_and_resample(df: pd.DataFrame) -> pd.DataFrame:
    """Resample to a strict hourly index per region, linearly interpolating gaps."""
    out = []
    for region, group in df.groupby("region"):
        group = group.set_index("timestamp").sort_index()
        full_index = pd.date_range(group.index.min(), group.index.max(), freq="h", tz="UTC")
        group = group.reindex(full_index)
        group["value"] = group["value"].interpolate(method="linear")
        group["region"] = region
        group.index.name = "timestamp"
        out.append(group.reset_index())
    return pd.concat(out, ignore_index=True)


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add hour-of-day, day-of-week, rolling stats, and week-over-week deviation.

    Expects columns: timestamp, region, value. Assumes one row per hour per region
    (run clean_and_resample first).
    """
    out = []
    for region, group in df.groupby("region"):
        group = group.sort_values("timestamp").reset_index(drop=True)

        group["hour_of_day"] = group["timestamp"].dt.hour
        group["day_of_week"] = group["timestamp"].dt.dayofweek

        group["rolling_mean_24h"] = (
            group["value"].rolling(window=ROLLING_WINDOW_HOURS, min_periods=1).mean()
        )
        group["rolling_std_24h"] = (
            group["value"].rolling(window=ROLLING_WINDOW_HOURS, min_periods=1).std()
        )

        same_hour_last_week = group["value"].shift(SAME_HOUR_LAST_WEEK_LAG)
        group["deviation_from_last_week"] = group["value"] - same_hour_last_week

        out.append(group)

    return pd.concat(out, ignore_index=True)
