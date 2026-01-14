# A-SOC: Aadhaar Security Operations Center

## Threat Intelligence System for Aadhaar Fraud Detection

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/Status-Production-green.svg" alt="Status">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
  <img src="https://img.shields.io/badge/Reproducible-Seed%2042-purple.svg" alt="Deterministic">
</p>

---

## 🎯 Overview

A-SOC is a **SOC-style Threat Intelligence System** for detecting potential Aadhaar fraud patterns using only official UIDAI enrollment, demographic update, and biometric update data.

This is **risk-based anomaly detection** for investigative prioritization - not a fraud confirmation system.

### Key Features

- 🔍 **PIN-level Risk Scoring**: Analyzes every PIN code for fraud indicators
- 📊 **IOC Detection**: Identifies 5 distinct fraud patterns automatically
- 🗺️ **Geographic Analysis**: State and district-level threat mapping
- ⏱️ **Temporal Analysis**: Detects enrollment/update spikes over time
- 📋 **Actionable Alerts**: Prioritized investigation queue with recommendations
- 🔒 **Fully Reproducible**: Deterministic output with fixed random seed

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- pip package manager

### Installation

```bash
# Clone or navigate to the project directory
cd "Aadhar hackathon"

# Install dependencies
pip install -r requirements.txt

# Run the analysis pipeline
python src/pipeline.py

# Launch the dashboard
streamlit run dashboards/streamlit_app.py
```

The dashboard will open at `http://localhost:8501`

---

## 📁 Project Structure

```
project_root/
├── data/
│   ├── api_data_aadhar_enrolment/     # Enrollment CSVs
│   ├── api_data_aadhar_demographic/   # Demographic update CSVs
│   └── api_data_aadhar_biometric/     # Biometric update CSVs
├── src/
│   ├── cleaning.py                    # Data loading & preprocessing
│   ├── features.py                    # Feature engineering
│   ├── risk_scoring.py                # Risk score calculation
│   ├── ioc_detection.py               # IOC pattern detection
│   ├── utils.py                       # Helper functions
│   └── pipeline.py                    # Main orchestration script
├── dashboards/
│   ├── streamlit_app.py               # Interactive SOC dashboard
│   └── tableau/
│       └── TABLEAU_SETUP.md           # Tableau configuration guide
├── outputs/
│   ├── risk_scores.csv                # PIN-level risk scores
│   ├── ioc_catalogue.csv              # Detected IOCs
│   ├── alerts.csv                     # Prioritized alerts
│   ├── state_summary.csv              # State-level aggregations
│   ├── district_summary.csv           # District-level aggregations
│   └── daily_summary.csv              # Time-series data
├── claude.md                          # System specification
├── dashboard.md                       # Dashboard specification
└── README.md                          # This file
```

---

## 📊 Risk Scoring Model

### Composite Risk Score Formula

```
Risk_Score = 
    (Enrollment_Velocity × 0.30) +
    (Update_Velocity × 0.25) +
    (Demographic_Anomaly × 0.20) +
    (Geographic_Outlier × 0.15) +
    (Temporal_Spike × 0.10)
```

### Risk Categories

| Level | Score Range | Action Required |
|-------|-------------|-----------------|
| **CRITICAL** | ≥ 8.0 | Immediate investigation |
| **HIGH** | 6.0 - 7.99 | Priority review within 48 hours |
| **MEDIUM** | 4.0 - 5.99 | Add to monitoring queue |
| **LOW** | < 4.0 | Normal activity |

---

## 🚨 IOC Detection Patterns

| Pattern | Code | Trigger Condition |
|---------|------|-------------------|
| Mass Enrollment Spike | MES | >400% increase in <7 days |
| Demographic Surge | DMS | >3× median updates |
| Biometric Churn | BIO | >30% recapture ratio |
| Child Ratio Anomaly | CRA | Z-score > 3 |
| Coordinated PIN Spike | CPS | High activity across all metrics |

---

## 🖥️ Dashboard Pages

1. **Overview** - Executive KPIs and risk distribution
2. **Threat Map** - Geographic risk visualization
3. **PIN Risk Explorer** - Deep-dive investigation mode
4. **Temporal Analysis** - Time-series patterns
5. **IOC Catalogue** - Threat intelligence library
6. **Data Health** - Quality metrics and validation
7. **Methodology** - Technical documentation

---

## 🔧 Configuration

### Environment Variables (Optional)

```bash
export ASOC_DATA_DIR="/path/to/data"
export ASOC_OUTPUT_DIR="/path/to/outputs"
```

### Random Seed

All random operations use seed `42` for reproducibility:
```python
np.random.seed(42)
```

---

## 📈 Output Files

### risk_scores.csv
PIN-level risk assessment with all features and scores.

| Column | Description |
|--------|-------------|
| pincode | 6-digit PIN code |
| state | State name |
| district | District name |
| risk_score | Composite score (0-10) |
| risk_level | CRITICAL/HIGH/MEDIUM/LOW |
| risk_factors | Top contributing factors |

### ioc_catalogue.csv
Detected Indicators of Compromise.

| Column | Description |
|--------|-------------|
| ioc_id | Unique identifier |
| pattern_name | Type of IOC detected |
| description | Detailed finding |
| recommended_action | Investigation guidance |

### alerts.csv
Prioritized alert queue for SOC analysts.

---

## 🔐 Data Integrity

This system follows strict rules:

- ✅ Uses **only** the three UIDAI datasets
- ❌ No external data sources
- ❌ No synthetic data generation
- ❌ No machine learning predictions
- ✅ All metrics are derived and explainable
- ✅ Deterministic output (same input → same output)

---

## 📋 Validation Checklist

- [x] Uses only 3 datasets (enrollment, demographic, biometric)
- [x] No external data enrichment
- [x] Risk scores are reproducible
- [x] IOC catalogue generated with actionable findings
- [x] Dashboard runs completely offline
- [x] All outputs are explainable

---

## 🛠️ Troubleshooting

### Pipeline fails to load data
```bash
# Check data directory structure
ls -la data/api_data_aadhar_*
```

### Dashboard shows no data
```bash
# Run the pipeline first
python src/pipeline.py

# Then launch dashboard
streamlit run dashboards/streamlit_app.py
```

### Memory issues with large datasets
```python
# Use chunked processing in cleaning.py
# Already implemented with glob pattern loading
```

---

## 📖 Methodology

This system implements **rule-based anomaly detection** rather than machine learning because:

1. **Explainability**: Every score traces to specific data points
2. **Auditability**: Fixed, documented rules
3. **No Training Data**: No labeled fraud cases available
4. **Transparency**: Investigators can challenge findings
5. **Reproducibility**: Deterministic with seed=42

For detailed methodology, see the **Methodology** page in the dashboard.

---

## 📄 License

MIT License - See LICENSE file for details.

---

## 🤝 Contributing

This is a demonstration project for the Aadhaar Hackathon.

---

## 📞 Support

For questions about the methodology or implementation, refer to:
- `claude.md` - System specification
- `dashboard.md` - Dashboard requirements
- Dashboard Methodology page - Technical documentation

---

<p align="center">
  <strong>Built for the Aadhaar Hackathon 2025</strong><br>
  A-SOC: Protecting India's Digital Identity Infrastructure
</p>
