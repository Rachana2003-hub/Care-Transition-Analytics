# Executive Summary
## Care Transition Efficiency & Placement Outcome Analytics

### Purpose
This project converts aggregate UAC program reporting data into an operational view of the care pipeline: CBP custody, transfer to HHS care, and discharge from HHS care.

### Dataset
The supplied file has 720 usable dated observations spanning 12 January 2023 through 21 December 2025, after removing 450 fully blank rows.

### What the dashboard provides
- Snapshot counts for CBP custody, HHS care, transfers, discharges and intake.
- Flow-to-stock indicators for transfers and discharges.
- Daily intake-minus-discharge pressure proxy.
- Monthly flow trends and weekday comparisons.
- Configurable visual thresholds and filtered CSV export.

### How stakeholders should use it
Use the dashboard to identify periods that merit operational review, compare trends over time, and ask where additional process-level data is needed. Alerts are screening signals, not performance verdicts.

### Key caveat
The available dataset contains aggregate daily counts rather than child-level timestamps or linked cases. It cannot directly calculate time from apprehension to HHS transfer, HHS length of stay, cohort-based placement rates, or placement durability. The displayed ratios are descriptive flow-to-stock indicators and must not be presented as direct reunification success rates.

### Recommended next steps
1. Add timestamped stage events and reconciled stock balances.
2. Track median and 90th-percentile time in CBP and HHS stages.
3. Report aged-case distributions and data completeness.
4. Validate thresholds with program experts before operational use.
5. Maintain strict privacy protections and prohibit individual-level decisions based on aggregate dashboard indicators.
