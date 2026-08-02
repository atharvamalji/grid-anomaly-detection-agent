import argparse
from pathlib import Path

import pandas as pd

from grid_agent.features import clean_and_resample, engineer_features
from grid_agent.ingestion import pull_and_store
from grid_agent.ingestion.pull import RAW_DATA_DIR
from grid_agent.models import AnomalyDetector


def load_or_pull(respondent: str, start: str, end: str) -> pd.DataFrame:
    """Pull data for the range if not already cached in data/raw/, then load it."""
    expected_path = RAW_DATA_DIR / f"{respondent}_{start}_{end}.parquet"
    if expected_path.exists():
        return pd.read_parquet(expected_path)
    path = pull_and_store(respondent, start, end)
    return pd.read_parquet(path)


def run_backtest(
    respondent: str,
    train_start: str,
    train_end: str,
    test_start: str,
    test_end: str,
) -> pd.DataFrame:
    """Fit on a baseline period, score a test period, and return flagged anomalies.

    train_end and test_start should typically be adjacent hours so the two
    periods are contiguous — e.g. train on a normal month, test on the days
    around a known event (heat wave, winter storm) for the demo narrative.
    """
    train_raw = load_or_pull(respondent, train_start, train_end)
    test_raw = load_or_pull(respondent, test_start, test_end)

    train_features = engineer_features(clean_and_resample(train_raw))
    test_features = engineer_features(clean_and_resample(test_raw))

    detector = AnomalyDetector()
    detector.fit(train_features)
    detector.save()

    results = detector.predict(test_features)
    anomalies = [r for r in results if r.is_anomaly]

    print(f"Scored {len(results)} hours; flagged {len(anomalies)} anomalies")
    for r in sorted(anomalies, key=lambda x: x.severity_score, reverse=True)[:10]:
        print(
            f"  {r.timestamp} [{r.region}] severity={r.severity_score:.3f} "
            f"value={r.contributing_features['value']:.0f} "
            f"wow_dev={r.contributing_features['deviation_from_last_week']:.0f}"
        )

    return pd.DataFrame(
        [
            {
                "timestamp": r.timestamp,
                "region": r.region,
                "is_anomaly": r.is_anomaly,
                "severity_score": r.severity_score,
                **r.contributing_features,
            }
            for r in results
        ]
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Train the Isolation Forest detector and backtest against a date range"
    )
    parser.add_argument("--respondent", default="MISO")
    parser.add_argument("--train-start", required=True, help='e.g. "2025-11-01T00"')
    parser.add_argument("--train-end", required=True, help='e.g. "2025-11-30T23"')
    parser.add_argument("--test-start", required=True, help='e.g. "2025-12-01T00"')
    parser.add_argument("--test-end", required=True, help='e.g. "2025-12-07T23"')
    parser.add_argument("--output", type=Path, default=None, help="Optional CSV output path")
    args = parser.parse_args()

    df = run_backtest(
        args.respondent,
        args.train_start,
        args.train_end,
        args.test_start,
        args.test_end,
    )

    if args.output:
        df.to_csv(args.output, index=False)
        print(f"Wrote full results to {args.output}")
