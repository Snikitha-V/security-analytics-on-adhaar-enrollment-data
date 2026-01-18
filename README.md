# A-SOC: Aadhaar Security Operations Center
## Fraud Detection and Threat Intelligence System

A comprehensive machine learning and rule-based system for detecting fraudulent Aadhaar enrollment patterns, demographic manipulation, and biometric anomalies at the PIN (pincode) level across India.

---

## 🎯 Project Overview

**A-SOC** analyzes ~5 million Aadhaar records across three data streams:
- **Enrollment Data**: New Aadhaar registrations by age group
- **Demographic Updates**: Changes to personal information
- **Biometric Recapture**: Fingerprint/iris updates and corrections

The system identifies fraud patterns through:
1. **Statistical Anomalies**: Z-score based outlier detection
2. **Velocity Analysis**: Activity relative to national medians
3. **Geographic Profiling**: District-level deviation scoring
4. **Temporal Detection**: Sudden activity spikes
5. **Rule-Based IOCs**: 8 fraud indicator patterns

---

## 📊 System Architecture

```
Raw Data (3 sources)
    ↓
Data Cleaning & Validation
    ↓
Feature Engineering (14 derived metrics)
    ↓
Risk Scoring (5-component weighted model)
    ↓
IOC Detection & Alerting
    ↓
Outputs (6 analytical datasets)
    ↓
Dashboards (Streamlit + React)
```

---

## 📁 Directory Structure

```
.
├── src/                          # Core Python modules
│   ├── cleaning.py              # Data loading & validation
│   ├── features.py              # Feature engineering
│   ├── pipeline.py              # Main orchestration
│   ├── risk_scoring.py          # Risk calculation
│   ├── ioc_detection.py         # Fraud pattern detection
│   └── utils.py                 # Helper functions
│
├── dashboards/                   # Analysis interfaces
│   ├── streamlit_app.py         # Interactive Streamlit dashboard
│   └── tableau/                 # Tableau configuration
│
├── frontend/                     # React.js web interface
│   ├── src/
│   │   ├── App.tsx              # Main React component
│   │   ├── lib/
│   │   │   ├── data.ts          # Data loading utilities
│   │   │   ├── geo.ts           # Geographic functions
│   │   │   └── queryClient.ts   # API client
│   │   └── ...
│   ├── package.json             # Dependencies
│   ├── vite.config.ts           # Build configuration
│   └── tailwind.config.js       # CSS configuration
│
├── data/                         # Raw datasets
│   ├── api_data_aadhar_enrolment/
│   ├── api_data_aadhar_demographic/
│   └── api_data_aadhar_biometric/
│
├── outputs/                      # Generated datasets
│   ├── risk_scores.csv
│   ├── alerts.csv
│   ├── daily_summary.csv
│   ├── district_summary.csv
│   ├── state_summary.csv
│   └── ioc_catalogue.csv
│
├── analysis.ipynb               # Statistical exploration notebook
├── government_intelligence.ipynb # Main analysis & visualizations
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+ (for frontend)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Snikitha-V/SECURITY-ANALYTICS-ON-AADHAAR-ENROLMENT-DATA-TRENDS-RISKS-AND-SYSTEM-INSIGHTS.git
   cd "Aadhar hackathon"
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the main pipeline**
   ```bash
   python src/pipeline.py
   ```

4. **Launch Streamlit dashboard**
   ```bash
   streamlit run dashboards/streamlit_app.py
   ```

5. **Run the analysis notebook**
   ```bash
   jupyter notebook government_intelligence.ipynb
   ```

---

## 📊 Output Datasets

| File | Records | Purpose |
|------|---------|---------|
| `risk_scores.csv` | 32,894 PINs | PIN-level risk assessment |
| `alerts.csv` | 4,079 alerts | High-priority investigation cases |
| `daily_summary.csv` | 115 days | Time-series trend analysis |
| `district_summary.csv` | 1,094 districts | Geographic rollup |
| `state_summary.csv` | 59 states | Executive dashboard |
| `ioc_catalogue.csv` | 49,787 IOCs | Fraud pattern indicators |

---

## 🎯 Risk Scoring Model

### Components (0-10 scale)
1. **Enrollment Velocity** (30%): Enrollments relative to national median
2. **Update Velocity** (25%): Demographic/biometric updates frequency
3. **Demographic Anomaly** (20%): Z-score based outlier detection
4. **Geographic Outlier** (15%): Deviation from district norms
5. **Temporal Spike** (10%): Sudden activity changes

### Risk Categories
| Category | Score | Action |
|----------|-------|--------|
| **CRITICAL** | ≥ 8.0 | Immediate investigation |
| **HIGH** | 6.0 - 7.99 | Priority review within 48 hours |
| **MEDIUM** | 4.0 - 5.99 | Scheduled audit |
| **LOW** | < 4.0 | Routine monitoring |

---

## 🔍 Fraud Indicators Detected

The system detects 8 fraud patterns (IOCs):

1. **Mass Enrollment Spike (MES)**: >400% increase in <7 days
2. **Demographic Surge (DMS)**: >3× median updates
3. **Biometric Churn (BIO)**: >30% recapture ratio
4. **Child Ratio Anomaly (CRA)**: Z-score > 3 in child enrollments
5. **Coordinated PIN Spike (CPS)**: Simultaneous activity spikes
6. **Ghost Enrollment (GHE)**: Suspicious elderly activity
7. **Operator Collusion (OPC)**: Extreme volume from single PIN
8. **Multi-PIN Synchronization (MPS)**: District-wide coordination

---

## 📈 Key Features

### Data Processing
- ✅ Chunked CSV loading (5M+ records)
- ✅ Automated schema standardization
- ✅ Pincode validation (6-digit regex)
- ✅ Date parsing and cleaning
- ✅ Missing value imputation

### Feature Engineering
- ✅ 14 derived metrics
- ✅ Velocity calculations
- ✅ Z-score anomaly detection
- ✅ Geographic profiling
- ✅ Temporal analysis

### Outputs
- ✅ Risk scores at multiple aggregation levels
- ✅ Detailed IOC catalogue
- ✅ Investigation-ready alerts
- ✅ Time-series trends
- ✅ Geographic heatmaps

### Visualizations
- ✅ Interactive Streamlit dashboard
- ✅ React.js web interface
- ✅ Tableau integration
- ✅ Geographic risk heatmaps
- ✅ Temporal trend analysis

---

## 🔧 Technology Stack

**Backend**
- Python 3.8+
- Pandas, NumPy, SciPy
- Scikit-learn

**Frontend**
- React.js with TypeScript
- Vite (build tool)
- Tailwind CSS
- Leaflet (maps)

**Dashboards**
- Streamlit
- Tableau

**Data Processing**
- Pandas (data manipulation)
- NumPy (numerical computing)
- SciPy (statistical functions)

---

## 📊 Analysis Notebooks

### `government_intelligence.ipynb` (46 cells)
Main analysis notebook featuring:
- Data exploration and profiling
- Risk score distribution analysis
- Geographic hotspot identification
- Temporal trend analysis
- Component comparison and attribution
- Multi-factor risk interactions
- Resource allocation recommendations

### `analysis.ipynb`
Supplementary statistical analysis and testing

---

## 🏗️ Pipeline Execution

The main pipeline (`src/pipeline.py`) executes in sequence:

```
1. Load & Clean Data      → 5M records validated
2. Merge Datasets         → Multiple aggregation levels
3. Engineer Features      → 14 derived metrics
4. Calculate Risk Scores  → Composite scoring model
5. Detect IOCs            → 8 fraud patterns
6. Generate Outputs       → 6 CSV files
7. Create Summaries       → Aggregated views
```

---

## 🔐 Data Security & Reproducibility

- **Deterministic Processing**: Fixed random seed (42) for reproducibility
- **No Machine Learning**: Rule-based detection for explainability
- **Percentile Capping**: 99th percentile normalization prevents outlier distortion
- **Schema Validation**: All inputs validated against specification

---

## 📝 Configuration & Customization

Key parameters in source files:

**Risk Thresholds** (`src/risk_scoring.py`):
```python
RISK_THRESHOLDS = {
    'CRITICAL': 8.0,
    'HIGH': 6.0,
    'MEDIUM': 4.0,
}
```

**IOC Patterns** (`src/ioc_detection.py`):
```python
IOC_PATTERNS = {
    'MES': {'threshold': 4.0, 'window_days': 7},
    'DMS': {'threshold': 3.0},
    'BIO': {'threshold': 0.30},
    # ... more patterns
}
```

---

## 📞 Support & Documentation

- **Data Pipeline**: See [DATA_README.md](DATA_README.md) for dataset descriptions
- **Methodology**: See [METHODOLOGY.md](METHODOLOGY.md) for technical approach
- **Specification**: See `claude.md` for system requirements

---

## 📄 License

[Specify your license here]

---

## 👥 Contributors

- **Project Team**: Aadhaar Security Operations Center
- **Data Source**: Official Aadhaar enrollment, demographic, and biometric records

---

## 🎓 Citation

If you use this system in research, please cite:

```
A-SOC: Aadhaar Security Operations Center
Fraud Detection and Threat Intelligence System
[Your Institution], 2024
```

---

**Last Updated**: January 2026  
**Version**: 1.0  
**Status**: Production Ready
