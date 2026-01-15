# FRONTEND REBUILD SPEC — LOCKED & FINAL

## Objective

Build a **from-scratch web frontend (React + Tailwind)** for Aadhaar Enrollment, Demographic, and Biometric **Fraud / Anomaly Detection**, replacing Streamlit/Tableau entirely.

The system must:

* visualize **every meaningful variable and derived feature**
* prioritize **visual explanations over tables**
* embed **formulas exactly where metrics are used**
* progressively build insight (raw → regional → national)
* look **non-generic, non-AI**, and academically serious
* work flawlessly with only the **provided datasets**

---

## TECH STACK (MANDATORY)

### Core

* React (Vite or Next.js App Router)
* TypeScript (strict mode)
* Tailwind CSS
* shadcn/ui (structure only)

### Visualization

* Recharts (primary)
* D3.js (advanced/custom views only)
* react-map-gl OR deck.gl (geospatial)

### State & Data

* TanStack Query (data loading)
* Zod (schema validation)
* Local JSON / Parquet preprocessing (no backend required initially)

---

## DATA SCOPE (HARD CONSTRAINT)

Use ONLY:

* Aadhaar Enrollment dataset
* Aadhaar Demographic Update dataset
* Aadhaar Biometric Update dataset

No synthetic data. No inferred personal attributes.

---

## INFORMATION ARCHITECTURE (NON-NEGOTIABLE)

### Level 0 — Data Familiarization

Purpose: prove data understanding before analysis

Visuals:

* Column completeness heatmap
* Record counts by dataset
* Temporal coverage timeline

No KPIs here.

---

### Level 1 — Variable-Level Visualization (CORE)

Every raw variable MUST be visualized.

For EACH numeric variable:

* Distribution histogram
* Percentile strip (P10 / P25 / Median / P75 / P90)
* Temporal trend (if time-indexed)

For EACH categorical variable:

* Ranked bar chart
* Geographic breakdown (if applicable)

Below EVERY visualization:

* Accordion: "How this metric is computed"

  * formula
  * source columns
* Accordion: "Why this matters"

  * fraud relevance
  * operational relevance
* Accordion: "What this does NOT prove"

---

### Level 2 — Feature Engineering Visuals

Derived features MUST be shown visually, not just described.

Examples:

* Enrollment velocity vs national median (bar + reference line)
* Update ratio (demographic / enrollment)
* Biometric recapture rate
* Age distribution divergence (KL-divergence visual)

Each derived feature requires:

* raw-input comparison chart
* derived-feature chart
* inline formula block

---

### Level 3 — Geographic Intelligence

Visuals:

* PIN-level choropleth (risk-normalized)
* District aggregation toggle
* Neighbor deviation plot (local vs surrounding PINs)

Interactivity:

* hover → local stats
* click → drill-down to variables

No tables unless ranking TOP / BOTTOM entities.

---

### Level 4 — Temporal & Correlation Analysis

Visuals:

* Multi-line temporal trends (enrollment / demo / bio)
* Lag-correlation plots
* Change-point markers
* Correlation heatmaps (annotated)

Explain correlation vs causation explicitly.

---

### Level 5 — Anomaly Detection Visualization

Without ML black boxes on landing views.

Show:

* Z-score distributions
* IQR fences
* Isolation Forest score distribution
* Cluster separation (2D projection)

Every anomaly view must show:

* why flagged
* relative extremeness
* comparison to national baseline

---

### Level 6 — Risk Scoring & National Synthesis

National stats appear ONLY here.

Visuals:

* Risk score distribution (PIN-level)
* Risk tier composition (stacked bars)
* National trend summary

Each national number must link back to:

* contributing variables
* geographic origin

---

## DESIGN SYSTEM (CREATIVE BUT DISCIPLINED)

### Color Semantics

* Enrollment → Teal
* Demographic → Amber
* Biometric → Indigo
* Anomaly → Crimson

No rainbow scales. No gradients.

### Layout Rules

* Wide analytical canvases
* Narrative left, charts right
* Asymmetry allowed

### shadcn/ui Usage

* Tabs → dataset switching
* Accordion → formulas & caveats
* Tooltip → assumptions
* Badge → risk tiers

No decorative components.

---

## TABLE USAGE (STRICTLY LIMITED)

Tables allowed ONLY for:

* top/bottom rankings
* comparisons across regions

Must have ≥ 3 meaningful columns.

---

## PERFORMANCE & QUALITY

* All charts must render under 200ms
* Memoize heavy computations
* Virtualize long lists
* Validate schemas at load time

---

## ACCEPTANCE CHECKLIST

The frontend is complete ONLY if:

* every raw variable is visualized
* every derived feature shows its inputs
* every formula is visible at point of use
* no meaningless tables exist
* UI does not resemble Streamlit/Tableau
* national stats are explainable end-to-end

---

## FINAL DIRECTIVE

Build this like a **real public-sector analytics system**, not a demo.
If a visualization cannot justify insight, remove it.
Clarity > cleverness.
