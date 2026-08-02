from pathlib import Path

import pandas as pd

from .eia_client import EIAClient

RAW_DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"


def records_to_dataframe(records: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(records)
    df["period"] = pd.to_datetime(df["period"], utc=True)
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.rename(columns={"period": "timestamp", "respondent": "region"})
    return df[["timestamp", "region", "value"]].sort_values("timestamp").reset_index(drop=True)


def pull_and_store(
    respondent: str,
    start: str,
    end: str,
    output_dir: Path = RAW_DATA_DIR,
) -> Path:
    """Pull hourly demand for a balancing authority and write it to Parquet.

    Output path: {output_dir}/{respondent}_{start}_{end}.parquet
    """
    client = EIAClient()
    records = client.fetch_hourly_demand(respondent, start, end)
    if not records:
        raise RuntimeError(f"No data returned for respondent={respondent}, {start}..{end}")

    df = records_to_dataframe(records)

    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"{respondent}_{start}_{end}.parquet"
    df.to_parquet(out_path, index=False)
    return out_path


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Pull hourly demand data from EIA-930")
    parser.add_argument("--respondent", default="MISO", help="Balancing authority code")
    parser.add_argument("--start", required=True, help='ISO date-hour, e.g. "2026-01-01T00"')
    parser.add_argument("--end", required=True, help='ISO date-hour, e.g. "2026-01-31T23"')
    args = parser.parse_args()

    path = pull_and_store(args.respondent, args.start, args.end)
    print(f"Wrote {path}")
