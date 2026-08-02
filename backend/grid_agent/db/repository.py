import json
import sqlite3
from pathlib import Path

from .models import DEFAULT_DB_PATH, get_connection


def insert_anomaly(
    conn: sqlite3.Connection,
    timestamp: str,
    region: str,
    severity_score: float,
    anomaly_type: str | None,
    explanation: str | None,
    recommendation: str | None,
    citations: list[str] | None,
    contributing_features: dict[str, float],
) -> int:
    cursor = conn.execute(
        """
        INSERT INTO anomalies
            (timestamp, region, severity_score, anomaly_type, explanation,
             recommendation, citations, contributing_features)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            timestamp,
            region,
            severity_score,
            anomaly_type,
            explanation,
            recommendation,
            json.dumps(citations or []),
            json.dumps(contributing_features),
        ),
    )
    conn.commit()
    return cursor.lastrowid


def get_recent_anomalies(
    limit: int = 20, db_path: Path = DEFAULT_DB_PATH
) -> list[dict]:
    conn = get_connection(db_path)
    try:
        rows = conn.execute(
            "SELECT * FROM anomalies ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
    finally:
        conn.close()

    results = []
    for row in rows:
        record = dict(row)
        record["citations"] = json.loads(record["citations"] or "[]")
        record["contributing_features"] = json.loads(record["contributing_features"] or "{}")
        results.append(record)
    return results


def get_anomaly_by_id(anomaly_id: int, db_path: Path = DEFAULT_DB_PATH) -> dict | None:
    conn = get_connection(db_path)
    try:
        row = conn.execute("SELECT * FROM anomalies WHERE id = ?", (anomaly_id,)).fetchone()
    finally:
        conn.close()

    if row is None:
        return None

    record = dict(row)
    record["citations"] = json.loads(record["citations"] or "[]")
    record["contributing_features"] = json.loads(record["contributing_features"] or "{}")
    return record
