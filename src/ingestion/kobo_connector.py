"""
ImpactTracker - KoboToolbox API Connector
Pulls survey data directly from KoboToolbox for automated MEL processing.
Author: Serge Nyamsin | MSc Data Science & AI, DSTI
"""

import requests
import pandas as pd
import logging
from typing import Optional
import os
KOBO_API_TOKEN = os.getenv("KOBO_API_TOKEN", "your_token_here")
KOBO_BASE_URL = os.getenv("KOBO_BASE_URL", "https://kobo.humanitarianresponse.info")

logger = logging.getLogger(__name__)


class KoboConnector:
    """
    Connects to KoboToolbox API to retrieve form submissions.
    Supports filtering by date, form, and status.
    """

    def __init__(self, api_token: str = None, base_url: str = None):
        self.token = api_token or KOBO_API_TOKEN
        self.base_url = base_url or KOBO_BASE_URL
        self.headers = {
            "Authorization": f"Token {self.token}",
            "Accept": "application/json"
        }

    def list_forms(self) -> pd.DataFrame:
        """List all available forms/assets."""
        url = f"{self.base_url}/api/v2/assets/"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        assets = response.json().get("results", [])
        return pd.DataFrame([{
            "uid": a["uid"],
            "name": a["name"],
            "submissions": a.get("deployment__submission_count", 0),
            "date_modified": a.get("date_modified")
        } for a in assets])

    def pull_data(
        self,
        form_uid: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 30000
    ) -> pd.DataFrame:
        """
        Pull all submissions for a given form.

        Args:
            form_uid: KoboToolbox form UID
            start_date: Filter from date (YYYY-MM-DD)
            end_date: Filter to date (YYYY-MM-DD)
            limit: Max records to retrieve
        """
        url = f"{self.base_url}/api/v2/assets/{form_uid}/data/"
        params = {"limit": limit, "format": "json"}

        if start_date:
            params["query"] = (
                f'{{"_submission_time":{{"$gte":"{start_date}"}}}}'
            )

        logger.info(f"Pulling data from KoboToolbox form: {form_uid}")
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()

        submissions = response.json().get("results", [])
        logger.info(f"Retrieved {len(submissions)} submissions")

        df = pd.DataFrame(submissions)
        df = self._clean_columns(df)
        return df

    def _clean_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove KoboToolbox internal metadata columns."""
        meta_cols = [
            c for c in df.columns
            if c.startswith("_") and c not in ["_id"]
        ]
        df = df.drop(columns=meta_cols, errors="ignore")
        if "_submission_time" in df.columns:
            df["submission_date"] = pd.to_datetime(
                df["_submission_time"]
            ).dt.date
        return df

    def export_to_csv(
        self,
        form_uid: str,
        output_path: str,
        **kwargs
    ) -> None:
        """Pull data and save to CSV."""
        df = self.pull_data(form_uid, **kwargs)
        df.to_csv(output_path, index=False)
        logger.info(f"Data exported to {output_path}")


class MockKoboConnector(KoboConnector):
    """Mock connector for testing without API credentials."""

    def pull_data(self, form_uid: str, **kwargs) -> pd.DataFrame:
        logger.info("Using MockKoboConnector — generating synthetic data")
        import numpy as np
        n = 500
        np.random.seed(42)
        return pd.DataFrame({
            "_id": range(1, n + 1),
            "submission_date": pd.date_range(
                "2024-01-01", periods=n, freq="D"
            ).date,
            "beneficiary_id": [f"BEN-{i:04d}" for i in range(1, n + 1)],
            "gender": np.random.choice(
                ["Male", "Female"], n, p=[0.45, 0.55]
            ),
            "age_group": np.random.choice(
                ["0-5", "6-17", "18-59", "60+"], n
            ),
            "OUT_001": np.random.choice([1, 0], n, p=[0.85, 0.15]),
            "OUT_002": np.random.randint(1, 5, n),
            "OUT_003": np.random.choice([1, 0], n, p=[0.70, 0.30]),
            "OUTC_001": np.random.choice([1, 0], n, p=[0.65, 0.35]),
            "OUTC_002": np.random.choice([1, 0], n, p=[0.60, 0.40]),
            "location": np.random.choice(
                ["Pristina", "Mitrovica", "Peja", "Prizren"], n
            ),
        })