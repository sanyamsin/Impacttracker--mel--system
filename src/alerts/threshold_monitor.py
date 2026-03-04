"""
ImpactTracker - Automated Alert & Threshold Monitor
Sends notifications when indicators fall below defined thresholds.
Author: Tresor | MSc Data Science & AI, DSTI
"""

import yaml
import logging
from typing import List
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class Alert:
    indicator_code: str
    indicator_name: str
    current_rate: float
    threshold: float
    severity: str
    message: str
    timestamp: datetime


class ThresholdMonitor:
    """
    Monitors indicator achievement rates against configured thresholds.
    Generates alerts for indicators at risk or in critical status.
    """

    SEVERITY_LEVELS = {
        "critical": {"threshold": 0.60, "color": "🔴"},
        "warning":  {"threshold": 0.85, "color": "⚠️"},
    }

    def __init__(self, config_path: str = "config/thresholds.yaml"):
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)
        logger.info("ThresholdMonitor initialized")

    def check_indicators(self, results: List) -> List[Alert]:
        """Check all indicator results and generate alerts."""
        alerts = []
        for result in results:
            rate = result.achievement_rate / 100

            if rate < self.SEVERITY_LEVELS["critical"]["threshold"]:
                severity = "critical"
            elif rate < self.SEVERITY_LEVELS["warning"]["threshold"]:
                severity = "warning"
            else:
                continue  # No alert needed

            alert = Alert(
                indicator_code=result.indicator.code,
                indicator_name=result.indicator.name,
                current_rate=result.achievement_rate,
                threshold=self.SEVERITY_LEVELS[severity]["threshold"] * 100,
                severity=severity,
                message=self._format_message(result, severity),
                timestamp=datetime.now()
            )
            alerts.append(alert)
            logger.warning(
                f"ALERT [{severity.upper()}]: "
                f"{result.indicator.code} at {result.achievement_rate}%"
            )

        return alerts

    def _format_message(self, result, severity: str) -> str:
        icon = self.SEVERITY_LEVELS[severity]["color"]
        action = (
            "Immediate intervention needed"
            if severity == "critical"
            else "Review and adjust activities"
        )
        return (
            f"{icon} [{severity.upper()}] {result.indicator.name}\n"
            f"   Achievement : {result.achievement_rate}% of target\n"
            f"   Status      : {result.status}\n"
            f"   Action      : {action}"
        )

    def generate_alert_report(self, alerts: List[Alert]) -> str:
        """Generate a full text alert report."""
        if not alerts:
            return "✅ All indicators on track — No alerts generated."

        critical_count = sum(
            1 for a in alerts if a.severity == "critical"
        )
        report = (
            f"📊 IMPACTTRACKER ALERT REPORT\n"
            f"Generated : {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
            f"{'=' * 60}\n\n"
            f"Total Alerts : {len(alerts)} "
            f"({critical_count} critical)\n\n"
        )

        for alert in sorted(alerts, key=lambda x: x.current_rate):
            report += alert.message + "\n\n"

        return report


if __name__ == "__main__":
    print("ThresholdMonitor ready ✅")