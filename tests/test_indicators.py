"""
ImpactTracker - Unit Tests for Indicator Engine
Author: Serge NYAMSIN | MSc Data Science & AI, DSTI
"""

import pandas as pd
import pytest
from unittest.mock import patch, mock_open
import yaml

# ── Mock Config ───────────────────────────────────────────────
MOCK_CONFIG = {
    "indicators": [
        {
            "code": "OUT_001",
            "name": "Beneficiaries trained",
            "level": "Output",
            "target": 100,
            "unit": "persons",
            "method": "sum",
            "disaggregation": []
        },
        {
            "code": "OUT_002",
            "name": "Training sessions conducted",
            "level": "Output",
            "target": 50,
            "unit": "sessions",
            "method": "sum",
            "disaggregation": []
        }
    ]
}

# ── Fixtures ──────────────────────────────────────────────────
@pytest.fixture
def mock_engine():
    with patch("builtins.open", mock_open(read_data=yaml.dump(MOCK_CONFIG))):
        from src.indicators.calculator import LogframeEngine
        return LogframeEngine("dummy_path.yaml")

@pytest.fixture
def data_on_track():
    return pd.DataFrame({
        "OUT_001": [1] * 90 + [0] * 10,   # 90% → On Track
        "OUT_002": [1] * 90 + [0] * 10,    # 90% → On Track
    })

@pytest.fixture
def data_at_risk():
    return pd.DataFrame({
        "OUT_001": [1] * 70 + [0] * 30,   # 70% → At Risk
        "OUT_002": [1] * 70 + [0] * 30,   # 70% → At Risk
    })

@pytest.fixture
def data_critical():
    return pd.DataFrame({
        "OUT_001": [1] * 40 + [0] * 60,   # 40% → Critical
        "OUT_002": [1] * 40 + [0] * 60,   # 40% → Critical
    })

# ── Tests : Calcul des indicateurs ───────────────────────────
def test_indicator_count(mock_engine, data_on_track):
    results = mock_engine.calculate(data_on_track)
    assert len(results) == 2

def test_achievement_rate_on_track(mock_engine, data_on_track):
    results = mock_engine.calculate(data_on_track)
    assert results[0].achieved == 90.0
    assert results[0].achievement_rate == 90.0

def test_achievement_rate_at_risk(mock_engine, data_at_risk):
    results = mock_engine.calculate(data_at_risk)
    assert results[0].achieved == 70.0
    assert results[0].achievement_rate == 70.0

# ── Tests : Statuts ───────────────────────────────────────────
def test_status_on_track(mock_engine, data_on_track):
    results = mock_engine.calculate(data_on_track)
    assert "On Track" in results[0].status

def test_status_at_risk(mock_engine, data_at_risk):
    results = mock_engine.calculate(data_at_risk)
    assert "At Risk" in results[0].status

def test_status_critical(mock_engine, data_critical):
    results = mock_engine.calculate(data_critical)
    assert "Critical" in results[0].status

# ── Tests : Colonnes manquantes ───────────────────────────────
def test_missing_column_returns_zero(mock_engine):
    data = pd.DataFrame({"OTHER_COL": [1, 2, 3]})
    results = mock_engine.calculate(data)
    assert results[0].achieved == 0.0

# ── Tests : to_dataframe ──────────────────────────────────────
def test_to_dataframe_columns(mock_engine, data_on_track):
    results = mock_engine.calculate(data_on_track)
    df = mock_engine.to_dataframe(results)
    expected_cols = [
        "Code", "Indicator", "Level", "Target",
        "Achieved", "Achievement Rate (%)", "Status"
    ]
    for col in expected_cols:
        assert col in df.columns

def test_to_dataframe_row_count(mock_engine, data_on_track):
    results = mock_engine.calculate(data_on_track)
    df = mock_engine.to_dataframe(results)
    assert len(df) == 2