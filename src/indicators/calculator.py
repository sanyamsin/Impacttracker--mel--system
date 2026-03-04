"""
ImpactTracker - Indicator Calculation Engine
Automates logframe-based indicator tracking for humanitarian programs.
Author: Serge Nyamsin | MSc Data Science & AI, DSTI
"""

import pandas as pd
import numpy as np
import yaml
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Indicator:
    code: str
    name: str
    level: str          # Output / Outcome / Impact
    target: float
    unit: str
    disaggregation: List[str]
    calculation_method: str


@dataclass
class IndicatorResult:
    indicator: Indicator
    achieved: float
    achievement_rate: float
    status: str         # On Track / At Risk / Critical
    last_updated: datetime
    trend: Optional[str] = None


class LogframeEngine:
    """
    Parse and process a logframe to auto-calculate indicator progress.
    """

    STATUS_THRESHOLDS = {
        "on_track": 0.85,
        "at_risk": 0.60,
    }

    def __init__(self, config_path: str):
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)
        self.indicators = self._parse_indicators()
        logger.info(f"Loaded {len(self.indicators)} indicators from logframe")

    def _parse_indicators(self) -> Dict[str, Indicator]:
        indicators = {}
        for ind in self.config.get("indicators", []):
            indicators[ind["code"]] = Indicator(
                code=ind["code"],
                name=ind["name"],
                level=ind["level"],
                target=float(ind["target"]),
                unit=ind.get("unit", ""),
                disaggregation=ind.get("disaggregation", []),
                calculation_method=ind.get("method", "count"),
            )
        return indicators

    def calculate(
        self,
        data: pd.DataFrame,
        period: str = None
    ) -> List[IndicatorResult]:
        """Calculate all indicators from collected data."""
        results = []
        for code, indicator in self.indicators.items():
            try:
                achieved = self._compute_value(indicator, data)
                rate = achieved / indicator.target if indicator.target > 0 else 0
                status = self._assess_status(rate)
                trend = self._compute_trend(code, achieved)

                results.append(IndicatorResult(
                    indicator=indicator,
                    achieved=achieved,
                    achievement_rate=round(rate * 100, 1),
                    status=status,
                    last_updated=datetime.now(),
                    trend=trend
                ))
                logger.info(
                    f"[{code}] {indicator.name}: "
                    f"{achieved}/{indicator.target} "
                    f"({rate*100:.1f}%) → {status}"
                )
            except Exception as e:
                logger.error(f"Error calculating {code}: {e}")

        return results

    def _compute_value(
        self,
        indicator: Indicator,
        data: pd.DataFrame
    ) -> float:
        col = indicator.code
        if col not in data.columns:
            logger.warning(f"Column '{col}' not found in data")
            return 0.0

        method = indicator.calculation_method
        if method == "count":
            return float(data[col].notna().sum())
        elif method == "sum":
            return float(data[col].sum())
        elif method == "mean":
            return float(data[col].mean())
        elif method == "percentage":
            total = len(data)
            return float(
                (data[col].sum() / total * 100) if total > 0 else 0
            )
        elif method == "unique_count":
            return float(data[col].nunique())
        else:
            return float(data[col].sum())

    def _assess_status(self, rate: float) -> str:
        if rate >= self.STATUS_THRESHOLDS["on_track"]:
            return "On Track ✅"
        elif rate >= self.STATUS_THRESHOLDS["at_risk"]:
            return "At Risk ⚠️"
        else:
            return "Critical 🔴"

    def _compute_trend(self, code: str, current: float) -> str:
        # Placeholder — in production, compare with historical DB
        return "→ Stable"

    def to_dataframe(
        self,
        results: List[IndicatorResult]
    ) -> pd.DataFrame:
        rows = []
        for r in results:
            rows.append({
                "Code": r.indicator.code,
                "Indicator": r.indicator.name,
                "Level": r.indicator.level,
                "Target": r.indicator.target,
                "Achieved": r.achieved,
                "Achievement Rate (%)": r.achievement_rate,
                "Unit": r.indicator.unit,
                "Status": r.status,
                "Trend": r.trend,
                "Last Updated": r.last_updated.strftime("%Y-%m-%d %H:%M"),
            })
        return pd.DataFrame(rows)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="ImpactTracker Indicator Calculator"
    )
    parser.add_argument(
        "--config",
        default="config/indicators_config.yaml"
    )
    parser.add_argument(
        "--data",
        default="data/processed/collected_data.csv"
    )
    parser.add_argument(
        "--output",
        default="data/reports/indicator_report.csv"
    )
    args = parser.parse_args()

    engine = LogframeEngine(args.config)
    data = pd.read_csv(args.data)
    results = engine.calculate(data)
    df = engine.to_dataframe(results)
    df.to_csv(args.output, index=False)
    print(df.to_string())
    print(f"\n✅ Report saved to {args.output}")