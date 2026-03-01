"""One-off backfill: train a per-region detector, run the agent on flagged
anomalies, and persist results to the shared DB — for regions beyond the
primary one whose model is served by the API (which uses a single shared
model path). Each region gets its own in-memory detector fit on its own
baseline period, since demand scale/patterns differ across balancing
authorities (a MISO-fitted detector would misread PJM's baseline as
anomalous, and vice versa).
"""

import argparse
import logging

from grid_agent.agent import analyze_anomaly
from grid_agent.db import get_connection, insert_anomaly
from grid_agent.features import clean_and_resample, engineer_features
from grid_agent.models import AnomalyDetector
from grid_agent.models.train import load_or_pull
from grid_agent.rag import RagIndex

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def backfill_region(
    respondent: str,
    train_start: str,
    train_end: str,
    test_start: str,
    test_end: str,
    rag_index: RagIndex,
) -> int:
    train_raw = load_or_pull(respondent, train_start, train_end)
    test_raw = load_or_pull(respondent, test_start, test_end)

    train_features = engineer_features(clean_and_resample(train_raw))
    test_features = engineer_features(clean_and_resample(test_raw))

    detector = AnomalyDetector()
    detector.fit(train_features)  # in-memory only — no save(), no shared model file

    results = detector.predict(test_features)
    flagged = [r for r in results if r.is_anomaly]
    print(f"[{respondent}] scored {len(results)} hours; flagged {len(flagged)} anomalies")

    conn = get_connection()
    inserted = 0
    try:
        for anomaly in flagged:
            try:
                state = analyze_anomaly(anomaly, rag_index=rag_index)
            except Exception:
                logger.exception(
                    "Agent analysis failed for %s anomaly at %s", respondent, anomaly.timestamp
                )
                state = {}

            insert_anomaly(
                conn,
                timestamp=str(anomaly.timestamp),
                region=anomaly.region,
                severity_score=anomaly.severity_score,
                anomaly_type=state.get("anomaly_type"),
                explanation=state.get("explanation"),
                recommendation=state.get("recommendation"),
                citations=state.get("citations", []),
                contributing_features=anomaly.contributing_features,
            )
            inserted += 1
    finally:
        conn.close()

    return inserted


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Backfill anomalies + agent explanations for comparison regions"
    )
    parser.add_argument(
        "--respondents",
        nargs="+",
        default=["PJM", "SWPP"],
        help="EIA-930 respondent codes (e.g. PJM, SWPP for Southwest Power Pool/SPP)",
    )
    parser.add_argument("--train-start", default="2025-08-01T00")
    parser.add_argument("--train-end", default="2025-10-31T23")
    parser.add_argument("--test-start", default="2025-11-01T00")
    parser.add_argument("--test-end", default="2026-01-31T23")
    args = parser.parse_args()

    index = RagIndex()
    index.load()

    for respondent in args.respondents:
        n = backfill_region(
            respondent,
            args.train_start,
            args.train_end,
            args.test_start,
            args.test_end,
            rag_index=index,
        )
        print(f"[{respondent}] inserted {n} anomalies with agent explanations")
