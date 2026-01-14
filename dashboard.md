Perfect — this is an important correction, and you’re **100% right** to demand this.

Below is a **FULL REWRITE of `dashboard.md`**, tuned so that:

* ❌ It does **not** look “AI-generated”
* ❌ It does **not** look like a toy Streamlit app
* ✅ It looks like a **real SOC internal dashboard**
* ✅ It is **informative, dense, credible, and polished**
* ✅ It uses **proven UI/UX patterns that humans actually design**
* ✅ Claude is **explicitly instructed how to think, design, and implement**

This version **overrides any earlier dashboard.md**.
Treat this as **FINAL & LOCKED**.

---

# 📊 `dashboard.md`

## A-SOC Operational Dashboard Specification (FINAL & LOCKED)

---

## 1. DESIGN PHILOSOPHY (NON-NEGOTIABLE)

This dashboard is **NOT a demo**, **NOT a portfolio app**, and **NOT a visual experiment**.

It represents an **internal Security Operations Center (SOC) tool** used daily by analysts.

### The Dashboard MUST:

* Prioritize **information density over decoration**
* Follow **human-designed enterprise UI patterns**
* Avoid anything that “looks automated” or “generated”
* Feel like it was designed by a **security analyst + data engineer**, not a designer

---

## 2. VISUAL IDENTITY (ANTI-AI RULESET)

Claude must follow these **strict UI constraints**.

### 2.1 Theme

* Dark mode only
* Matte background (no gradients)
* Low saturation, high contrast
* No neon colors

**Base Colors**

* Background: `#0E1117`
* Panels: `#161B22`
* Borders: `#30363D`
* Text primary: `#E6EDF3`
* Text secondary: `#8B949E`

---

### 2.2 Risk Color System (SOC-Standard)

| Risk Level | Color     | Usage            |
| ---------- | --------- | ---------------- |
| CRITICAL   | `#D73A49` | Alerts, hotspots |
| HIGH       | `#F85149` | Warning states   |
| MEDIUM     | `#DBAB09` | Monitoring       |
| LOW        | `#2EA043` | Normal           |

⚠️ These colors are **semantic**, not decorative.
They must **never be repurposed**.

---

### 2.3 Typography Rules

* Default font: **system font stack**
* No custom fonts
* No playful weights
* No excessive sizing

**Hierarchy**

* Section headers: Medium, small
* KPI values: Bold, compact
* Tables: Dense, readable
* Tooltips: Minimal, factual

---

## 3. DASHBOARD STRUCTURE (HUMAN-FIRST)

The dashboard is **modular**, not scroll-heavy.

### Layout Philosophy

* Analysts scan **left → right, top → bottom**
* Critical signals first
* Details on demand

---

## 4. GLOBAL NAVIGATION (LEFT SIDEBAR)

Use `streamlit-option-menu`.

### Navigation Items (Fixed Order)

1. **Overview**
2. **Threat Map**
3. **PIN Risk Explorer**
4. **Temporal Analysis**
5. **IOC Catalogue**
6. **Data Health**
7. **Methodology**

No hidden pages.
No dynamic generation.

---

## 5. PAGE-BY-PAGE SPECIFICATION

---

### 5.1 OVERVIEW — “SOC AT A GLANCE”

**Purpose:**
Immediate situational awareness for senior analysts.

#### Top KPI Strip (Cards)

Use clean metric cards (no icons).

* Total PIN Codes Monitored
* Critical Risk PINs
* High Risk PINs
* Estimated Fraud Exposure (₹)
* Last Data Refresh (date only)

Cards must:

* Be compact
* Have subtle borders
* Use risk color only when applicable

---

#### National Risk Trend (Primary Chart)

**Chart:** Line chart
**X:** Date
**Y:** National Composite Risk Index

Overlay:

* Moving average (7-day)
* Highlight anomaly dates

This is the **main executive signal**.

---

#### Alerts Summary Table

**Table columns:**

* PIN Code
* State
* Risk Score
* Risk Level
* Primary Trigger (text)
* First Detected (date)

Rules:

* Sort by Risk Score (desc)
* Color only the Risk Level column
* Click row → navigate to PIN Explorer

---

### 5.2 THREAT MAP — “WHERE IS RISK CONCENTRATED”

**Purpose:** Geographic threat intelligence.

#### Map Type

* Choropleth map (State-level)
* Bubble overlay (PIN-level hotspots)

**Color:**

* State fill = average risk score
* Bubble size = severity

Tooltips must include:

* State
* Avg Risk
* # Critical PINs
* Dominant risk factor

❌ No animation
❌ No satellite maps

---

### 5.3 PIN RISK EXPLORER — “INVESTIGATION MODE”

**Purpose:** Deep dive into a single PIN code.

#### PIN Selector

* Searchable dropdown
* No free text

---

#### Risk Breakdown Panel

**Stacked horizontal bar**

* Enrollment Velocity
* Update Velocity
* Demographic Anomaly
* Geographic Outlier
* Temporal Anomaly

Each component labeled with:

* Score
* Short explanation (static text)

---

#### Time Series Panel

3 aligned plots:

1. Enrollment volume
2. Demographic updates
3. Biometric updates

Shared X-axis (time).
Analysts should visually confirm correlations.

---

#### Context Table

Shows:

* Neighboring PIN averages
* National median
* Deviation %

---

### 5.4 TEMPORAL ANALYSIS — “WHEN DOES RISK SPIKE”

**Purpose:** Identify coordinated operations.

#### Heatmap

* Rows: States
* Columns: Months
* Color: Avg Risk

---

#### Spike Detection Table

Columns:

* Date
* Affected PINs
* Avg Risk Jump %
* Likely Cause (rule-based label)

---

### 5.5 IOC CATALOGUE — “THREAT INTELLIGENCE”

This page mirrors a **real SOC IOC library**.

#### IOC Table

Columns:

* IOC ID
* Pattern Name
* Detection Rule (plain text)
* Risk Level
* First Seen
* Affected PIN Count

No charts here.
SOC tools rely on **tables, not visuals**.

---

### 5.6 DATA HEALTH — “TRUST THE SIGNAL”

**Purpose:** Prove credibility.

Metrics:

* Missing values %
* Outliers detected
* Rows processed
* Validation checks passed

Include:

* Last validation run timestamp
* Known limitations (static text)

---

### 5.7 METHODOLOGY — “DEFENSIBLE ANALYTICS”

This page is judge-facing.

Contents:

* Risk score formula
* Indicator weights
* Why each indicator exists
* False positive mitigation strategy
* Why no black-box ML is used

---

## 6. INTERACTION RULES (VERY IMPORTANT)

Allowed:

* Filters
* Hover tooltips
* Drill-down via selection

Forbidden:

* Sliders with animations
* Gimmicks
* Auto-refresh
* Sound / motion

---

## 7. WHAT MAKES THIS LOOK HUMAN (EXPLICIT)

Claude must ensure:

* Slight asymmetry in layout (not perfect grids)
* Dense tables with real numbers
* Labels that sound like analysts wrote them
* No marketing language
* No “smart”, “AI-powered”, “next-gen” phrasing

If something looks “cool” but adds no insight → **remove it**.

---

## 8. FINAL HARD CONSTRAINTS

* Use **ONLY** the three UIDAI datasets provided
* No synthetic data
* No placeholders
* No lorem ipsum
* Every chart must justify its existence

---

## 🔐 FINAL LOCK STATEMENT

This dashboard specification is **FINAL**.

If Claude encounters ambiguity:

> **Clarity > aesthetics**
> **Information > impressiveness**
> **SOC realism > visual flair**
