# Web Style Guide — Fraud & Anomaly Analytics Platform

> **Goal:** Analyst-first, credible, and calm. No flashy AI aesthetics. Prioritize clarity, density, and trust.

---

## 1. Design Principles

* **Truth over theatrics:** Every visual must map directly to data.
* **Dense but readable:** Information-rich layouts with disciplined spacing.
* **Explainable by default:** Tooltips, captions, and definitions everywhere.
* **Consistent parity:** Visual semantics must translate 1:1 to Tableau.

**Avoid:** neon gradients, glassmorphism, excessive animations, oversized hero cards.

---

## 2. Color System (Accessible & Professional)

### Core Palette

* **Background:** #0F172A (slate-900)
* **Surface:** #111827 (gray-900)
* **Panel:** #1F2933 (gray-800)
* **Border:** #334155 (slate-700)

### Text

* **Primary:** #E5E7EB (gray-200)
* **Secondary:** #9CA3AF (gray-400)
* **Muted:** #6B7280 (gray-500)

### Semantic Accents

* **High Risk:** #DC2626 (red-600)
* **Medium Risk:** #F59E0B (amber-500)
* **Low Risk:** #10B981 (emerald-500)
* **Info:** #3B82F6 (blue-500)

> Contrast ratio ≥ 4.5:1 for all text.

---

## 3. Typography

* **Primary:** Inter (UI, labels, body)
* **Monospace:** JetBrains Mono (IDs, hashes, metrics)

### Scale

* H1: 24px / 700
* H2: 20px / 600
* H3: 16px / 600
* Body: 14px / 400
* Caption: 12px / 400

Line-height: 1.4–1.6

---

## 4. Layout System

### Grid

* 12-column responsive grid
* Max width: 1280px
* Gutters: 16px

### Page Structure

1. Header (context + filters)
2. KPI strip (compact, comparable)
3. Primary analysis (charts/tables)
4. Supporting diagnostics
5. Footnotes & definitions

---

## 5. Components

### KPI Cards

* Flat panels (no gradients)
* Large metric + delta
* Clear definition tooltip
* Color only for delta or severity

### Tables (Primary)

* Zebra rows (#0B1220 / #0F172A)
* Sticky headers
* Right-aligned numbers
* Column-level tooltips

### Charts

* Default to bar/line/heatmap
* No 3D, no donut abuse
* Axis labels always visible
* Annotate anomalies explicitly

---

## 6. Interaction & Motion

* **Motion:** Minimal (150–200ms ease-out)
* **Hover:** Highlight + tooltip only
* **Click:** Drill-down, not modal spam

No autoplay, no looping animations.

---

## 7. Filters & Controls

* Global filters pinned (date, region, center)
* Multi-select with search
* Show active filters as chips
* One-click reset

---

## 8. Data Semantics & Labels

Every metric must include:

* Definition
* Calculation logic
* Data source
* Refresh cadence
  nDisplayed as tooltip or info icon.

---

## 9. Error & Empty States

* Explicit message: what’s missing and why
* No skeleton loaders pretending data exists
* Offer next best view using available fields

---

## 10. Accessibility

* Keyboard navigable
* ARIA labels for charts
* Color not sole indicator
* Font scaling supported

---

## 11. Streamlit Implementation Notes

* Use `st.container()` for sections
* Avoid `st.metric()` overuse
* Prefer `st.dataframe()` with column configs
* Custom CSS only for spacing & colors

---


## 13. What This Should Feel Like

* A government analytics portal
* A SOC investigation console
* A data science capstone — not a demo

If a visual cannot be explained in one sentence, redesign it.
