# Aadhaar Fraud Detection - Security Analytics

## 🎯 Overview

This repository contains a comprehensive Jupyter notebook for analyzing **Aadhaar enrollment data** to detect fraud patterns, identify high-risk regions, and support government decision-making.

**Dataset Scale:**
- 📊 **1M+ Enrollment Records** - New Aadhaar registrations by age group
- 📊 **2M+ Demographic Updates** - Address and name change requests
- 📊 **1.8M+ Biometric Updates** - Fingerprint and iris re-capture events
- 📊 **32,894 PIN Codes** - Risk-scored at granular geographic level

---

## 📁 Repository Structure

```
.
├── government_intelligence.ipynb   # Main analysis notebook (46 cells)
├── requirements.txt                # Python dependencies
├── README.md                       # This file
│
├── data/                           # Raw Aadhaar datasets
│   ├── api_data_aadhar_enrolment/     # Enrollment CSVs (~1M records)
│   ├── api_data_aadhar_demographic/   # Demographic update CSVs (~2M records)
│   └── api_data_aadhar_biometric/     # Biometric update CSVs (~1.8M records)
│
└── outputs/                        # Pre-computed analysis results
    ├── risk_scores.csv             # PIN-level risk assessment (32,894 PINs)
    ├── alerts.csv                  # High-priority investigation targets
    ├── daily_summary.csv           # Time-series aggregation
    ├── district_summary.csv        # District-level rollups
    ├── state_summary.csv           # State-level summary
    └── ioc_catalogue.csv           # Indicators of Compromise
```

---

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/Akhilucky/Aadhar-data-Security-Analytics.git
cd Aadhar-data-Security-Analytics
```

### 2. Create Virtual Environment (Recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Launch Jupyter Notebook
```bash
jupyter notebook government_intelligence.ipynb
```

### 5. Run All Cells
- Click **Kernel > Restart & Run All** to execute the complete analysis
- Total execution time: ~2-3 minutes

---

## 📦 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| pandas | ≥1.5.0 | Data manipulation |
| numpy | ≥1.23.0 | Numerical computing |
| matplotlib | ≥3.6.0 | Static visualizations |
| seaborn | ≥0.12.0 | Statistical plots |
| scipy | ≥1.9.0 | Statistical functions |

Install all with:
```bash
pip install pandas numpy matplotlib seaborn scipy jupyter
```

---

## 📊 Analysis Sections

The notebook contains **10 analytical sections**:

| Section | Title | Key Visualizations |
|---------|-------|-------------------|
| 1 | Data Loading | Schema inspection, record counts |
| 2 | Data Cleaning | Quality checks, date parsing |
| 3 | Executive Summary | 6-panel dashboard with key metrics |
| 4 | Risk Distribution | State-wise risk heatmaps |
| 5 | Component Analysis | 5-factor risk breakdown |
| 6 | Multi-Factor Analysis | X+Y→Z interaction matrices |
| 7 | Age Demographics | Ghost enrollment detection |
| 8 | Statistical Analysis | Distribution curves, Z-scores |
| 9 | Geographic Hotspots | District-level risk mapping |
| 10 | Temporal Trends | Year-over-year spike detection |

---

## 🎯 Risk Scoring Model

### Formula
```
Risk Score = 0.30×EV + 0.25×UV + 0.20×DA + 0.15×GO + 0.10×TS
```

### Components (0-10 scale each)
| Code | Component | Weight | What It Measures |
|------|-----------|--------|------------------|
| EV | Enrollment Velocity | 30% | Enrollments vs national median |
| UV | Update Velocity | 25% | Demographic update frequency |
| DA | Demographic Anomaly | 20% | Z-score based outlier detection |
| GO | Geographic Outlier | 15% | Deviation from district norms |
| TS | Temporal Spike | 10% | Sudden activity changes |

### Risk Categories
| Category | Score Range | Recommended Action |
|----------|-------------|-------------------|
| 🔴 **HIGH** | ≥ 6.0 | Priority investigation within 48 hours |
| 🟡 **MEDIUM** | 3.0 - 5.99 | Scheduled audit |
| 🟢 **LOW** | < 3.0 | Routine monitoring |

---

## 📈 Key Findings (Sample)

From the pre-computed analysis:

- **High-Risk PINs:** 4,079 PINs flagged for investigation
- **Top Risk States:** Uttar Pradesh, Maharashtra, Bihar lead in absolute count
- **Common Pattern:** High enrollment velocity + demographic surge = fraud indicator
- **Temporal Insight:** Weekend activity drops may indicate legitimate patterns

---

## 🔧 Customization

### Change Data Path
Edit cell 2 in the notebook:
```python
base_path = Path('/your/custom/path/to/data')
```

### Adjust Risk Thresholds
The risk levels are defined as:
```python
HIGH_THRESHOLD = 6.0    # Change to adjust sensitivity
MEDIUM_THRESHOLD = 3.0
```

### Add New Visualizations
The notebook uses matplotlib/seaborn. Add new cells following the existing pattern:
```python
fig, ax = plt.subplots(figsize=(14, 6))
# Your visualization code
plt.tight_layout()
plt.show()
```

---

## 📝 Data Dictionary

### Raw Data Columns

**Enrollment Data (`api_data_aadhar_enrolment/*.csv`)**
| Column | Type | Description |
|--------|------|-------------|
| date | string | Date in DD-MM-YYYY format |
| state | string | State name |
| district | string | District name |
| pincode | string | 6-digit postal code |
| age_0_5 | int | Enrollments age 0-5 years |
| age_5_17 | int | Enrollments age 5-17 years |
| age_18_greater | int | Enrollments age 18+ years |

**Demographic Data (`api_data_aadhar_demographic/*.csv`)**
| Column | Type | Description |
|--------|------|-------------|
| date | string | Date in DD-MM-YYYY format |
| state | string | State name |
| district | string | District name |
| pincode | string | 6-digit postal code |
| demo_age_5_17 | int | Updates for age 5-17 |
| demo_age_18_greater | int | Updates for age 18+ |

**Biometric Data (`api_data_aadhar_biometric/*.csv`)**
| Column | Type | Description |
|--------|------|-------------|
| date | string | Date in DD-MM-YYYY format |
| state | string | State name |
| district | string | District name |
| pincode | string | 6-digit postal code |
| bio_age_5_17 | int | Biometric updates age 5-17 |
| bio_age_18_greater | int | Biometric updates age 18+ |

### Output Data Columns

**Risk Scores (`outputs/risk_scores.csv`)**
| Column | Description |
|--------|-------------|
| pincode | 6-digit postal code |
| state, district | Geographic identifiers |
| risk_score | Composite score (0-10) |
| risk_level | Category (LOW/MEDIUM/HIGH) |
| enrollment_velocity | Component score |
| update_velocity | Component score |
| demographic_anomaly | Component score |
| geographic_outlier | Component score |
| temporal_spike | Component score |

---

## 🔒 Data Security Notes

- All data is **aggregated at PIN level** - no individual Aadhaar numbers
- Analysis is **deterministic** (random seed = 42) for reproducibility
- No machine learning models - pure **rule-based detection** for explainability

---

## 📄 License

This project is for educational and research purposes.
    
