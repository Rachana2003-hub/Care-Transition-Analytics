# Care Transition Efficiency & Placement Outcome Analytics

An interactive Streamlit dashboard for aggregate UAC program reporting data.

## Run locally
1. Install Python 3.10 or later.
2. Open a terminal in this project folder.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the dashboard:
   ```bash
   streamlit run app.py
   ```
5. Open the local URL printed in the terminal (usually http://localhost:8501).

## Project contents
- `app.py` — Streamlit dashboard with filters, KPIs, charts, alerts and CSV export.
- `data/uac_care_data.csv` — cleaned copy of the supplied dataset.
- `reports/` — EDA report, executive summary and methodology notes.
- `requirements.txt` — Python dependencies.

## Metrics and interpretation
- Transfer indicator = daily children transferred out of CBP / children in CBP custody.
- Discharge indicator = daily children discharged from HHS / children in HHS care.
- Intake–discharge pressure = daily apprehensions minus daily HHS discharges.
- Cumulative exits/entries = sum of HHS discharges / sum of apprehensions in the selected period.

These are descriptive operational indicators. Same-day flow divided by a stock is not a cohort conversion rate, elapsed-time measure, or proof of successful reunification. Intake minus discharge is a pressure proxy, not a reconciled backlog balance. The source dataset does not include child-level case IDs, timestamps for each stage, sponsor details, or case durations.

## Data handling
The app drops completely blank rows, parses dates, removes comma separators from numeric fields, sorts chronologically and removes duplicate dates (keeping the last record). It does not impute missing operational counts.

## Suggested future enhancements
- Add case-level timestamps to calculate median/90th percentile CBP-to-HHS transfer time and HHS length of stay.
- Reconcile opening stock + inflows - outflows = closing stock for each stage.
- Add facility/location and sponsor-type dimensions if lawfully available and privacy-protected.
- Add data validation, automated tests, audit logging and role-based access for production deployment.

## Responsible use
Use aggregate outputs for operational review only. Do not use this dashboard to rank individual children, infer personal characteristics, or make decisions about a child's eligibility or care.
