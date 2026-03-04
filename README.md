# 🎯 ImpactTracker — Automated MEL System

> An end-to-end automated Monitoring, Evaluation & Learning platform for humanitarian and development programs.

[![MEL Pipeline](https://github.com/sanyamsin/Impacttracker--mel--system/actions/workflows/mel_pipeline.yml/badge.svg)](https://github.com/sanyamsin/Impacttracker--mel--system/actions/workflows/mel_pipeline.yml)
[![Tests](https://github.com/sanyamsin/Impacttracker--mel--system/actions/workflows/tests.yml/badge.svg)](https://github.com/sanyamsin/Impacttracker--mel--system/actions/workflows/tests.yml)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🌍 Overview

ImpactTracker automates the full MEL cycle for humanitarian programs:
- **Data Collection** → KoboToolbox API integration
- **Indicator Calculation** → Logframe-based automated tracking
- **Progress Monitoring** → Real-time vs target comparison
- **Automated Alerts** → Threshold-based notifications
- **Reporting** → Automated CSV/Excel donor reports
- **Learning** → Trend analysis & recommendations

## 🏗️ Architecture
```
Data Sources (KoboToolbox / ODK / Excel)
              ↓
      Data Ingestion Layer
              ↓
    Processing & Validation
              ↓
    Indicator Engine (Logframe)
              ↓
  ┌───────────────────────────┐
  │  Dashboard (Streamlit)    │
  │  Automated Reports        │
  │  Alert System             │
  └───────────────────────────┘
```

## 📊 Key Features

| Feature | Description |
|---------|-------------|
| Logframe Automation | Parse logframes, auto-calculate output/outcome indicators |
| KoboToolbox Integration | Direct API pull from field data collection |
| Progress Tracking | Real-time achievement rate vs targets |
| Donor Reporting | Auto-generate ECHO, UNHCR, USAID-format reports |
| Alert System | Email/Slack alerts when indicators below threshold |
| CI/CD Pipeline | Weekly automated data pull & report generation |

## 🚀 Quick Start
```bash
# Clone & setup
git clone https://github.com/sanyamsin/Impacttracker--mel--system.git
cd Impacttracker--mel--system

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Run dashboard
streamlit run dashboards/app.py
```

## 📁 Project Structure
```
impacttracker-mel-system/
├── src/
│   ├── ingestion/          # KoboToolbox & ODK connectors
│   ├── processing/         # Data cleaning & validation
│   ├── indicators/         # Logframe & indicator engine
│   ├── visualization/      # Charts & report generation
│   └── alerts/             # Threshold monitoring & notifications
├── dashboards/             # Streamlit MEL dashboard
├── config/                 # Indicators, thresholds, settings
├── data/                   # Raw, processed, reports
├── tests/                  # Unit tests (9/9 passing)
└── .github/workflows/      # CI/CD automation
```

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Data Processing | Python, Pandas, NumPy |
| Dashboard | Streamlit, Plotly |
| Field Data | KoboToolbox API |
| Testing | Pytest (9/9 passing) |
| CI/CD | GitHub Actions |
| Containerization | Docker |

## 📸 Dashboard Preview

> MEL Dashboard with real-time indicator tracking, disaggregation by gender/location, and automated alerts.

## 👤 Author

**Serge Nyamsin** | Data Scientist | 12+ years humanitarian field experience

- 🎓 MSc Data Science & AI — Data ScienceTech Institute (DSTI)
- 🌍 Field experience: CAR, Senegal, Mauritania, Niger, Mali, Burkina Faso
- 💼 Data Science Intern — Innovation Center Kosovo
- 🔗 [GitHub](https://github.com/sanyamsin)

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.