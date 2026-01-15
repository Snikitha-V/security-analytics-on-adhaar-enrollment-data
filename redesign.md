# FRONTEND INSTRUCTIONS (LOCKED)

## Purpose

Create a **data-dense, non-generic, analyst-grade web interface** for Aadhaar Enrollment, Demographic, and Biometric fraud/anomaly detection that:

* prioritizes **visual explanations over tables**
* embeds **formulas exactly where metrics appear**
* builds insight progressively (variable → regional → national)
* introduces **creative but disciplined visual identity** (NOT generic dashboards)
* preserves existing layout and structure (no breaking changes)

---

## DESIGN PHILOSOPHY (NON-GENERIC BUT SERIOUS)

### Visual Identity Goal

The UI should feel like:

* a **modern government analytics portal**
* a **SOC investigation console**
* a **graduate-level data science system**

NOT:

* SaaS landing page
* startup demo
* auto-generated Streamlit app

---

## CREATIVE COLOR SYSTEM (ALLOWED & ENCOURAGED)

### Base Palette (Anchor)

* Background: Near-black charcoal (#0E1117)
* Primary text: Soft off-white (#E6E8EB)
* Secondary text: Muted gray (#9AA0A6)

### Analytical Accent Colors (Use Intentionally)

* Enrollment metrics: Muted Teal (#4FB6B2)
* Demographic patterns: Desaturated Amber (#E0B15C)
* Biometric signals: Cool Indigo (#6C7FF2)
* Risk / anomaly: Deep Crimson (#C44536)
* Neutral reference lines: Slate Blue-Gray (#6B7280)

Rules:

* Never use rainbow palettes
* Never encode >1 variable with color in a single chart
* Color must encode **meaning**, not decoration

---

## DESIGN ELEMENTS (NON-GENERIC UI)

### Layout Principles

* Asymmetry is allowed (break card grids subtly)
* Prefer **wide analytical canvases** over tall stacks
* Use left-aligned narrative blocks, not center alignment

### shadcn/ui (MANDATORY USE CASES)

Use shadcn ONLY for structure and clarity:

* Accordion → formulas, assumptions, limitations
* Tabs → switching variables (Enrollment / Demographic / Biometric)
* Badge → risk tiers (Low / Medium / High / Critical)
* Tooltip → statistical assumptions, caveats

Do NOT:

* change fonts
* add rounded “startup” cards
* add animations beyond subtle hover/expand

---

## DATA VISUALIZATION RULES (CRITICAL)

### 1. NO MEANINGLESS TABLES

Tables are ONLY allowed if they:

* compare or rank entities (top/bottom PINs, districts)
* have >= 3 meaningful columns

If a table shows:

* raw schema
* a single populated column
* data without comparison

→ it must be replaced with a visualization.

---

### 2. VISUAL-FIRST ANALYSIS FLOW (MANDATORY)

For EACH variable or metric:

1. **Primary Visualization**

   * Histogram / ranked bar / line / heatmap
2. **Inline Stats Strip (NOT a table)**

   * Mean | Median | Std Dev | Percentiles
3. **Formula Accordion (Directly Below Chart)**

   * Exact formula
   * Inputs used (from provided datasets ONLY)
   * Interpretation
   * Limitations
4. **Why This Is Useful**

   * Fraud relevance
   * Operational value

---

### 3. FORMULA-IN-CONTEXT RULE (NON-NEGOTIABLE)

Formulas must appear **exactly where the metric is visualized**.

Example structure:

[Chart]
[Stats strip]
[Accordion: "How this metric is computed"]
[Accordion: "Why this matters for fraud detection"]

No global formula pages allowed.

---

## PROGRESSIVE DISCLOSURE FLOW

### Level 1: Variable-Level Understanding

* One metric at a time
* Distribution-focused visuals
* No aggregation beyond necessity

### Level 2: Regional Context

* State / District comparisons
* Choropleths and ranked bars
* Highlight deviations, not totals

### Level 3: National Synthesis (ONLY AFTER ABOVE)

* Aggregated risk distribution
* National trend lines
* Cross-dataset correlation summaries

National KPIs must NEVER appear on landing page.

---

## EXPLANATION STANDARD (REQUIRED TEXT BLOCK)

Every visualization must include a short narrative answering:

1. What pattern is visible?
2. Why is this pattern useful?
3. What it does NOT prove (guard against overclaiming)

This text must be concise, neutral, and analytical.

---

## FRONTEND CONSTRAINTS (LOCKED)

* Do NOT change page structure
* Do NOT change navigation
* Do NOT change typography
* Do NOT add generic cards or hero sections

Enhancement must come ONLY from:

* better visual encodings
* better explanations
* disciplined creative color use

---

## DATA SCOPE CONSTRAINT

You MUST use ONLY the following datasets:

* Aadhaar Enrollment data
* Aadhaar Demographic Update data
* Aadhaar Biometric Update data

No synthetic data.
No assumptions outside these datasets.

---

## SUCCESS CRITERIA

The frontend is successful if:

* A reviewer can trace every national insight back to raw variables
* No visualization exists without explanation
* No table exists without comparison value
* The UI feels intentional, not auto-generated

---

## FINAL INSTRUCTION TO COPILOT

Follow this file strictly.
If a visualization or table cannot justify its existence, remove it.
Creativity is encouraged ONLY within analytical discipline.
