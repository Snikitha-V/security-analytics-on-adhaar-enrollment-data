Perfect. Below is the **FINAL, LOCKED, NO-AMBIGUITY Claude.md**.
This is the version you can paste into **Claude Opus** and trust that:

* it will **not hallucinate**
* it will **use only your datasets**
* it will **build a reproducible, runnable, SOC-grade project**
* it will **not invent data, APIs, maps, or assumptions**
* it will **produce Tableau + Streamlit + IOC catalogue correctly**

This is effectively a **spec + contract**.

---

# 🔒 A-SOC_CLAUDE.md — FINAL & LOCKED (v1.1)

> **NON-NEGOTIABLE SYSTEM CONTRACT**
> This document is the single source of truth.
> Claude MUST follow every rule in this file exactly.
> No assumptions, no external data, no deviations.

---

## 0. ABSOLUTE RULES (READ FIRST)

1. **USE ONLY THE PROVIDED DATASETS**

   * Enrollment dataset
   * Demographic Updates dataset
   * Biometric Updates dataset
     ❌ No external datasets
     ❌ No synthetic data
     ❌ No APIs
     ❌ No shapefiles
     ❌ No enrichment from internet or assumptions

2. **NO FIELD CREATION EXCEPT DERIVED METRICS**

   * You may ONLY create:

     * Aggregations
     * Ratios
     * Z-scores
     * Velocities
     * Risk scores
   * You may NOT invent columns such as income, gender, fraud labels, device IDs, operator IDs, etc.

3. **ALL ANALYSIS MUST BE EXPLAINABLE**

   * Every metric must map directly to:

     * Enrollment
     * Demographic updates
     * Biometric updates

4. **PROJECT MUST RUN OFFLINE**

   * No internet calls
   * No geocoding APIs
   * No cloud dependencies

5. **DETERMINISTIC OUTPUT**

   * Fixed random seeds
   * Same input → same output every run

---

## 1. PROJECT PURPOSE (LOCKED)

Build a **SOC-style Threat Intelligence System** for detecting **potential Aadhaar fraud patterns** using **only enrollment, demographic update, and biometric update data**.

This is **NOT** a prediction of confirmed fraud.
This is **risk-based anomaly detection** for investigative prioritization.

The system must:

* Identify abnormal patterns
* Assign explainable risk scores
* Surface alerts via dashboards
* Provide investigator-ready context

---

## 2. DATASETS (STRICT SCHEMA)

### 2.1 Enrollment Dataset

**Columns (exact):**

* Date
* State
* District
* PIN
* Age_0_5
* Age_5_17
* Age_18_greater

### 2.2 Demographic Updates Dataset

**Columns (exact):**

* Date
* State
* District
* PIN
* Demo_age_5_17
* Demo_age_18_greater

### 2.3 Biometric Updates Dataset

**Columns (exact):**

* Date
* State
* District
* PIN
* Bio_age_5_17
* Bio_age_18_greater

❗ If any column is missing or null → treat as **0**, not dropped.

---

## 3. DATA HANDLING RULES (MANDATORY)

### 3.1 Date Handling

* Parse Date as `datetime`
* Granularity = **daily**
* All time-series analysis operates at **PIN + Date**

### 3.2 Aggregation Rules

* Primary unit of analysis = **PIN code**
* Secondary rollups = District → State → National
* Aggregation order:

  1. Clean
  2. Normalize
  3. Aggregate
  4. Analyze

### 3.3 Missing / Zero Values

* Missing → 0
* Division by zero → safe-guarded (return 0, not NaN)

---

## 4. FEATURE ENGINEERING (ONLY THESE)

### 4.1 Core Metrics

* Total_Enrollments = Age_0_5 + Age_5_17 + Age_18_greater
* Total_Demo_Updates = Demo_age_5_17 + Demo_age_18_greater
* Total_Bio_Updates = Bio_age_5_17 + Bio_age_18_greater

### 4.2 Ratios

* Child_Ratio = Age_0_5 / Total_Enrollments
* Update_Ratio = Total_Demo_Updates / Total_Enrollments
* Bio_Recapture_Ratio = Total_Bio_Updates / Total_Enrollments

### 4.3 Velocity Metrics

* Enrollment_Velocity = PIN_Total_Enrollments / National_Median_Enrollments
* Update_Velocity = PIN_Total_Updates / National_Median_Updates
* Bio_Velocity = PIN_Total_Bio_Updates / National_Median_Bio

### 4.4 Statistical Anomalies

* Z-score applied ONLY to:

  * Child_Ratio
  * Update_Ratio
  * Bio_Recapture_Ratio
* Z-scores clipped to ±5

---

## 5. RISK SCORING MODEL (LOCKED)

### 5.1 Risk Components (0–10 scale)

| Component               | Weight |
| ----------------------- | ------ |
| Enrollment Velocity     | 0.30   |
| Update Velocity         | 0.25   |
| Demographic Anomaly (Z) | 0.20   |
| Geographic Outlier      | 0.15   |
| Temporal Spike          | 0.10   |

### 5.2 Composite Risk Score

```
Risk_Score =
(Enroll_Velocity * 0.30) +
(Update_Velocity * 0.25) +
(Demo_Z * 0.20) +
(Geo_Outlier * 0.15) +
(Time_Spike * 0.10)
```

### 5.3 Risk Categories

* **Critical:** ≥ 8
* **High:** 6 – 7.99
* **Medium:** 4 – 5.99
* **Low:** < 4

---

## 6. FRAUD IOC CATALOGUE (MANDATORY OUTPUT)

### IOC RULES (NO DEVIATION)

| IOC Pattern           | Trigger                   |
| --------------------- | ------------------------- |
| Mass Enrollment Spike | >400% increase in <7 days |
| Demographic Surge     | >3× median updates        |
| Biometric Churn       | >30% recapture            |
| Child Ratio Anomaly   | Z-score > 3               |
| Coordinated PIN Spike | High enroll + demo + bio  |

Each IOC must include:

* PIN
* District
* State
* Date range
* Risk score
* Recommended action

---

## 7. TABLEAU DASHBOARD (STRICT)

### Constraints

* Use **Tableau built-in maps only**
* No shapefiles
* No external joins
* All calculations derived from dataset fields

### Required Sheets

1. National Threat Heatmap
2. Threat Timeline
3. Enrollment vs Update Scatter
4. Demographic & Biometric Anomaly Monitor
5. SOC Alert Queue (table)

### Required Filters

* Date range
* State
* District
* Risk level

---

## 8. STREAMLIT DASHBOARD (STRICT)

### Runtime Rules

* Python ≥ 3.10
* Libraries:

  * pandas
  * numpy
  * plotly
  * scikit-learn
  * streamlit
* No internet
* Fixed random seed = 42

### Required Sections

* Executive KPI strip
* Interactive map (aggregated)
* Temporal anomaly chart
* Correlation scatter
* Alert table (exportable)

---

## 9. REQUIRED FOLDER STRUCTURE (MANDATORY)

```
project_root/
├── data/
│   ├── enrollment.csv
│   ├── demographic_updates.csv
│   └── biometric_updates.csv
├── src/
│   ├── cleaning.py
│   ├── features.py
│   ├── risk_scoring.py
│   ├── ioc_detection.py
│   └── utils.py
├── dashboards/
│   ├── streamlit_app.py
│   └── tableau/
├── outputs/
│   ├── risk_scores.csv
│   ├── alerts.csv
│   └── ioc_catalogue.csv
└── README.md
```

---

## 10. FINAL VALIDATION CHECKLIST (MUST PASS ALL)

* [ ] Uses only 3 datasets
* [ ] No external data
* [ ] Risk score reproducible
* [ ] IOC catalogue generated
* [ ] Tableau dashboard matches spec
* [ ] Streamlit app runs offline
* [ ] All outputs explainable

---

## 🔐 FINAL NOTE (LOCK)

If any instruction conflicts:

> **This file overrides all other reasoning.**

Claude must **ask no clarifying questions** and must **execute exactly as specified**.

---