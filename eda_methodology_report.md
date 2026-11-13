# Exploratory Data Analysis & Methodology

## 1. Dataset overview
The supplied CSV contains 1,170 physical rows and 720 usable dated records after removing 450 fully blank rows. The usable date range is **12 January 2023 to 21 December 2025**. There are six source fields: reporting date, daily apprehensions/intake, CBP custody stock, transfers out of CBP, HHS care stock, and HHS discharges.

The source file contains trailing fully blank rows. The HHS care field is stored as text with thousands separators, so preprocessing removes commas and converts it to numeric. Dates are parsed and sorted chronologically. No missing values are filled with fabricated values.

## 2. Analysis questions
1. How do reported CBP and HHS care loads change over time?
2. How do daily transfers and discharges vary?
3. How do flow-to-stock indicators change over time?
4. Are there periods where daily intake persistently exceeds HHS discharges?
5. Do weekday patterns appear in aggregate daily movements?

## 3. Metric definitions
- **Transfer indicator:** daily transfers out of CBP divided by same-day CBP custody stock.
- **Discharge indicator:** daily HHS discharges divided by same-day HHS care stock.
- **Intake–discharge pressure:** daily apprehensions minus daily HHS discharges.
- **Selected-period exits/entries:** total HHS discharges divided by total apprehensions.

### Important metric limitation
The transfer and discharge indicators are flow-to-stock ratios. They are not true transition probabilities because the numerator and denominator are not linked to the same child cohort. They do not measure elapsed time. Likewise, intake minus HHS discharges is only a high-level system pressure proxy: apprehensions enter the CBP stage while discharges leave HHS, and transfers between stages and reporting cut-offs affect the stock balance. A true backlog calculation requires reconciled opening/closing stocks and all stage-specific inflows/outflows.

## 4. EDA summary
Descriptive statistics for the numeric fields:

|       |   Children apprehended and placed in CBP custody* |   Children in CBP custody |   Children transferred out of CBP custody |   Children in HHS Care |   Children discharged from HHS Care |
|:------|--------------------------------------------------:|--------------------------:|------------------------------------------:|-----------------------:|------------------------------------:|
| count |                                            720    |                    720    |                                    720    |                 720    |                              720    |
| mean  |                                             93.52 |                    171.49 |                                    128.67 |                6061.28 |                              173.41 |
| std   |                                             72.65 |                    126.35 |                                     97.32 |                2833.07 |                              125.7  |
| min   |                                              0    |                      7    |                                      0    |                1972    |                                0    |
| 25%   |                                             12    |                     36    |                                     14    |                2467.75 |                               19.75 |
| 50%   |                                             99    |                    193    |                                    157    |                6406.5  |                              181    |
| 75%   |                                            147.25 |                    263.25 |                                    199.25 |                8010.25 |                              267    |
| max   |                                            333    |                    531    |                                    440    |               11516    |                              505    |

## 5. Methodology
1. Load the CSV using Pandas.
2. Remove fully blank rows.
3. Parse `Date` into a datetime field.
4. Convert count fields to numeric after removing comma separators.
5. Sort records by date and inspect missingness/duplicates.
6. Calculate descriptive flow-to-stock indicators and intake–discharge pressure.
7. Aggregate counts by month and weekday.
8. Visualize stocks, flows, ratios, and pressure trends.
9. Apply configurable visual alert thresholds.
10. Interpret results with explicit data limitations.

## 6. Recommended operational improvements
- Capture event timestamps at apprehension, HHS intake, medical screening completion, case-management milestones, sponsor approval and discharge.
- Calculate median and 90th-percentile time in each stage, segmented by facility and case complexity only where lawful and privacy-safe.
- Reconcile daily stage balances using opening stock + inflows − outflows = closing stock.
- Monitor aged-case bands (for example, days in stage) rather than relying only on aggregate counts.
- Track data completeness and reporting latency as dashboard KPIs.
- Review alerts with program staff; do not treat thresholds as automatic evidence of poor performance.

## 7. Limitations and ethical considerations
This is aggregate administrative data. It does not contain individual case records, case-level elapsed times, sponsor characteristics, placement quality, or reasons for delay. Therefore, the analysis cannot establish causality or evaluate the quality or durability of a placement. The dashboard is intended for system-level monitoring and policy discussion, not individual-level decisions.
