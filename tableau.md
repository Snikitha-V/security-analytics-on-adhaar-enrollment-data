# 🖥️ A-SOC: TABLEAU DASHBOARD SPEC

**Dashboard Name:** A-SOC | National Identity Threat Intelligence

---

## SHEETS & LOGIC

1. **National Threat Heatmap**  
   - Map: PIN code level (aggregated to districts if needed)  
   - Color: Risk Level (Green: Low, Yellow: Medium, Orange: High, Red: Critical)  
   - Tooltip: Total Enrollments, Updates, Risk Score, Top IOC  

2. **Threat Timeline**  
   - X-axis: Date  
   - Y-axis: Risk Score / Alert Count  
   - Filters: State, District, Risk Level  

3. **Enrollment vs Update Correlation**  
   - Scatter Plot: Enrollment Velocity vs Update Velocity  
   - Color: Risk Level  
   - Tooltip: Child Ratio, Biometric Updates  

4. **Demographic & Biometric Anomaly Monitor**  
   - Rows: PIN Codes  
   - Columns: Age group ratios, update counts  
   - Highlight: Z-score > 3 or abnormal recapture  

5. **SOC Alert Queue (Table)**  
   - Columns: PIN, District, Risk Score, IOC Pattern, Suggested Action  
   - Filters: Risk Level, State, Date  

---

## CALCULATED FIELDS

- **Enrollment Velocity** = (PIN_Total_Enrollments / National_Median_Enroll)  
- **Update Velocity** = (PIN_Total_Updates / National_Median_Updates)  
- **Child Ratio Z** = Z-score(Age_0_5 / Total_Enrollments)  
- **Composite Risk Score** = Enrollment_Velocity*0.3 + Update_Velocity*0.25 + Demographic_Anomaly*0.2 + Geographic_Outlier*0.15 + Temporal_Anomaly*0.1  
- **Risk Category** = IF Score ≥8 → Critical, 6-7.9 → High, 4-5.9 → Medium, <4 → Low  

---

## FILTERS & ACTIONS

- **Filters:** Date Range, State, District, Risk Level, Dataset Source  
- **Actions:**  
  - Drilldown (Map → District → PIN)  
  - Color-coded risk brushing  
  - Dynamic sync across all sheets  

---

## KPI STRIP (Executive Summary)

- Total PINs flagged  
- Critical Alerts  
- Avg Risk Score  
- Top 5 High-Risk Districts  
- Financial Impact Estimate (₹)  
- Social Impact Estimate (people protected)
