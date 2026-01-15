# NOTEBOOK → FRONTEND EXECUTION SPEC (LOCKED)

## PURPOSE (READ FIRST)

This file defines the **only acceptable workflow** for building this project.

The notebook is the **truth filter**. The website is the **delivery mechanism**.

If a metric, visualization, or feature is not justified in the notebook, it **must not exist** in the frontend.

This spec prioritizes:

* signal over completeness
* explainability over flash
* decision-impact over aesthetics

---

## NON-NEGOTIABLE RULES

1. **No visualization without a question**

   * Every plot must explicitly answer a real analytical or operational question.

2. **Variables must earn survival**
   Each variable must be classified as:

   * ACTIONABLE (production)
   * CONTEXTUAL (explanatory only)
   * REJECTED (dropped permanently)

3. **Aggressive pruning is mandatory**
   Expect to discard **50–70%** of initial ideas.

4. **Micro → Macro ONLY**

   * Variable → Local → Regional → National
   * Never start from national aggregates.

5. **No decorative charts**
   If a chart does not change prioritization, risk scoring, or investigation focus, it is invalid.

---

## NOTEBOOK STRUCTURE (STRICT)

### 1. INTRODUCTION (Markdown)

* Dataset scope and provenance
* Real-world risks in Aadhaar enrollment, demographic updates, biometrics
* Explicit questions this notebook answers

---

### 2. DATA INGESTION & SANITY CHECKS

**Code Only**

* Schema validation
* Missing value profiling
* Cardinality checks
* Basic range validation

**Markdown**

* Known data limitations
* What this data cannot prove

---

### 3. VARIABLE REVIEW LOOP (REPEATABLE BLOCK)

For EACH variable or logical feature group:

#### a. Definition (Markdown)

* What it represents
* Units / scale
* Real-world relevance

#### b. Distribution Analysis (Code)

* Histogram / KDE
* Box / violin plot
* Extreme percentiles (1, 5, 95, 99)

#### c. Statistical Summary (Code)

* Mean, median, std
* Skewness, kurtosis
* Outlier proportion

#### d. Interpretation (Markdown)

* What normal looks like
* What abnormal might indicate
* Possible non-fraud explanations

#### e. Verdict (Markdown – REQUIRED)

Choose ONE:

* ✅ ACTIONABLE
* ⚠️ CONTEXTUAL
* ❌ REJECTED

Justify the decision in 2–3 sentences.

---

### 4. DERIVED FEATURES & FRAUD SIGNALS

Only build features that combine or transform validated variables.

For EACH derived metric:

* Explicit mathematical formula
* Visualization
* Operational meaning
* Assumptions
* Failure modes

Examples:

* Enrollment velocity anomaly
* Demographic mutation frequency
* Biometric re-capture intensity

---

### 5. TEMPORAL & SPATIAL PATTERNS

* Time-series with rolling baselines
* Region-wise deviation plots

Explain:

* seasonality vs anomalies
* operational spikes vs suspicious spikes

---

### 6. ANOMALY DETECTION (LIMITED & JUSTIFIED)

Allowed models ONLY:

* Z-score baselines
* Isolation Forest
* LOF

For each model:

* Why this model fits the data
* What the score means (NOT accuracy)
* Comparison with statistical baselines

No labels. No fake precision claims.

---

### 7. AGGREGATION TO NATIONAL INSIGHTS

Only after ALL prior validation.

Show:

* Contribution of local anomalies to national risk
* Pareto effects (top X% → Y% risk)

---

### 8. PRODUCTION APPROVAL LIST (MANDATORY)

Final Markdown section:

#### APPROVED FOR FRONTEND

* Feature name
* Metric definition
* Visualization type
* Intended user decision

#### REJECTED FEATURES

* Feature name
* Why it was rejected

This list is FINAL.

---

## FRONTEND TRANSLATION RULES

* Frontend must implement **ONLY approved features**

* Every visualization must:

  * expose its formula (tooltip or modal)
  * explain why it matters
  * state assumptions

* No placeholder tables

* No single-column meaningless summaries

---

## DESIGN PHILOSOPHY FOR FRONTEND

* Investigative, not dashboard-y
* Semantic color encoding (risk, deviation, confidence)
* Progressive disclosure
* Tables only when comparison is required
* Visuals must dominate, text explains

---

## FINAL WARNING

If Copilot generates:

* generic KPIs
* unexplained charts
* filler tables
* national summaries without buildup

Those outputs are INVALID and must be discarded.

This project succeeds by **discipline, not volume**.

---

## END OF SPEC (DO NOT MODIFY)
