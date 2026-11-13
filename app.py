
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title="Care Transition Analytics", page_icon="🧭", layout="wide")

st.markdown("""
<style>
.main {background-color:#f7f9fc;}
[data-testid="stMetric"] {background:#ffffff;padding:14px;border:1px solid #e5eaf2;border-radius:12px;}
.block-container {padding-top:1.5rem;}
</style>
""", unsafe_allow_html=True)

st.title("🧭 Care Transition Efficiency & Placement Outcome Analytics")
st.caption("UAC care pipeline monitoring | CBP custody → HHS care → sponsor discharge")
st.info("This dashboard analyzes aggregate program counts. Ratios are operational indicators, not individual child outcomes, causal estimates, or direct measures of reunification quality.")

DEFAULT_FILE = Path(__file__).parent / "data" / "uac_care_data.csv"

@st.cache_data
def load_data(uploaded_file=None):
    if uploaded_file is not None:
        x = pd.read_csv(uploaded_file)
    else:
        x = pd.read_csv(DEFAULT_FILE)
    x = x.dropna(how="all").copy()
    x["Date"] = pd.to_datetime(x["Date"], errors="coerce")
    for col in x.columns:
        if col != "Date":
            x[col] = pd.to_numeric(x[col].astype(str).str.replace(",", "", regex=False), errors="coerce")
    x = x.dropna(subset=["Date"]).sort_values("Date").drop_duplicates("Date", keep="last")
    return x.reset_index(drop=True)

uploaded = st.sidebar.file_uploader("Upload a replacement CSV (optional)", type=["csv"])
try:
    df = load_data(uploaded)
except Exception as e:
    st.error(f"Could not load the dataset: {e}")
    st.stop()

COLS = {
    "intake": "Children apprehended and placed in CBP custody*",
    "cbp": "Children in CBP custody",
    "transfers": "Children transferred out of CBP custody",
    "hhs": "Children in HHS Care",
    "discharges": "Children discharged from HHS Care",
}
missing = [v for v in COLS.values() if v not in df.columns]
if missing:
    st.error("The uploaded file is missing required columns: " + ", ".join(missing))
    st.stop()

st.sidebar.header("Filters")
min_date, max_date = df.Date.min().date(), df.Date.max().date()
date_range = st.sidebar.date_input("Reporting date range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    view = df[df.Date.between(start, end)].copy()
else:
    view = df.copy()

metric_mode = st.sidebar.radio("Ratio display", ["Percent", "Raw ratio"], horizontal=True)
transfer_threshold = st.sidebar.slider("Low transfer indicator threshold (%)", 0, 100, 20)
discharge_threshold = st.sidebar.slider("Low discharge indicator threshold (%)", 0, 100, 5)
rolling_days = st.sidebar.slider("Rolling average window (records)", 3, 30, 7)

if view.empty:
    st.warning("No records are available for this date range.")
    st.stop()

# Metric definitions: stock-normalized daily flow indicators, not true cohort conversion rates.
view["transfer_ratio"] = view[COLS["transfers"]] / view[COLS["cbp"]].replace(0, np.nan)
view["discharge_ratio"] = view[COLS["discharges"]] / view[COLS["hhs"]].replace(0, np.nan)
view["entries"] = view[COLS["intake"]]
view["exits"] = view[COLS["discharges"]]
view["net_pressure"] = view["entries"] - view["exits"]
view["transfer_pct"] = view["transfer_ratio"] * 100
view["discharge_pct"] = view["discharge_ratio"] * 100
view["transfer_roll"] = view["transfer_pct"].rolling(rolling_days, min_periods=1).mean()
view["discharge_roll"] = view["discharge_pct"].rolling(rolling_days, min_periods=1).mean()

def latest_valid(series):
    s = series.dropna()
    return float(s.iloc[-1]) if len(s) else np.nan

def fmt_num(x):
    return "—" if pd.isna(x) else f"{x:,.0f}"

def fmt_pct(x):
    if pd.isna(x): return "—"
    return f"{x:.1f}%" if metric_mode == "Percent" else f"{x/100:.3f}"

st.subheader("Program snapshot")
last = view.iloc[-1]
a,b,c,d,e = st.columns(5)
a.metric("CBP custody", fmt_num(last[COLS["cbp"]]), help="Children reported in CBP custody on the latest selected date.")
b.metric("HHS care", fmt_num(last[COLS["hhs"]]), help="Children reported in HHS care on the latest selected date.")
c.metric("Daily transfers", fmt_num(last[COLS["transfers"]]))
d.metric("Daily discharges", fmt_num(last[COLS["discharges"]]))
e.metric("Daily intake", fmt_num(last[COLS["intake"]]))

st.caption(f"Selected records: {len(view):,} | Date coverage: {view.Date.min():%d %b %Y} – {view.Date.max():%d %b %Y}")

st.divider()
st.subheader("1. Care pipeline flow")
f1, f2, f3 = st.columns(3)
with f1:
    st.metric("CBP → HHS transfer indicator", fmt_pct(latest_valid(view["transfer_pct"])))
with f2:
    st.metric("HHS discharge indicator", fmt_pct(latest_valid(view["discharge_pct"])))
with f3:
    st.metric("Cumulative exits / entries", fmt_pct(100*view["exits"].sum()/view["entries"].sum()) if view["entries"].sum() else "—")

flow = pd.DataFrame({
    "Stage": ["CBP custody (latest)", "HHS care (latest)", "Discharges (latest day)"],
    "Children": [last[COLS["cbp"]], last[COLS["hhs"]], last[COLS["discharges"]]]
})
fig = px.bar(flow, x="Stage", y="Children", color="Stage", title="Latest reported pipeline counts")
fig.update_layout(showlegend=False, yaxis_title="Children (reported count)")
st.plotly_chart(fig, use_container_width=True)

st.divider()
st.subheader("2. Transfer and discharge efficiency indicators")
ratio_choice = st.radio("Choose indicator", ["Transfer indicator", "Discharge indicator"], horizontal=True)
if ratio_choice == "Transfer indicator":
    y, roll, title = "transfer_pct", "transfer_roll", "Daily transfers ÷ CBP custody"
else:
    y, roll, title = "discharge_pct", "discharge_roll", "Daily discharges ÷ HHS care"
fig = go.Figure()
fig.add_trace(go.Scatter(x=view.Date, y=view[y], mode="lines+markers", name="Daily indicator", connectgaps=False))
fig.add_trace(go.Scatter(x=view.Date, y=view[roll], mode="lines", name=f"{rolling_days}-record rolling average"))
fig.update_layout(title=title, xaxis_title="Date", yaxis_title="Ratio (%)", hovermode="x unified")
st.plotly_chart(fig, use_container_width=True)

st.divider()
st.subheader("3. Backlog pressure and bottleneck signals")
st.caption("Daily intake minus daily HHS discharges is a system pressure proxy only. It is not a reconciled backlog balance because the measures refer to different stages and may have reporting/transfer timing differences.")
fig = px.bar(view, x="Date", y="net_pressure", title="Daily intake minus HHS discharges", color="net_pressure", color_continuous_scale="RdYlBu_r")
fig.add_hline(y=0, line_dash="dash", line_color="black")
st.plotly_chart(fig, use_container_width=True)

cbp_fig = go.Figure()
cbp_fig.add_trace(go.Scatter(x=view.Date, y=view[COLS["cbp"]], mode="lines", name="CBP custody"))
cbp_fig.add_trace(go.Scatter(x=view.Date, y=view[COLS["hhs"]], mode="lines", name="HHS care"))
cbp_fig.update_layout(title="Reported active care loads over time", xaxis_title="Date", yaxis_title="Children")
st.plotly_chart(cbp_fig, use_container_width=True)

st.divider()
st.subheader("4. Placement outcome trends")
monthly = view.set_index("Date").resample("MS").agg({
    COLS["intake"]: "sum", COLS["transfers"]: "sum",
    COLS["discharges"]: "sum", COLS["cbp"]: "mean", COLS["hhs"]: "mean"
}).reset_index()
monthly = monthly.rename(columns={COLS["intake"]:"Intake", COLS["transfers"]:"Transfers", COLS["discharges"]:"Discharges"})
fig = px.line(monthly, x="Date", y=["Intake","Transfers","Discharges"], markers=True, title="Monthly intake, transfer and discharge volumes")
st.plotly_chart(fig, use_container_width=True)

weekday = view.copy()
weekday["Weekday"] = weekday.Date.dt.day_name()
weekday_summary = weekday.groupby("Weekday", as_index=False).agg(
    Avg_Transfers=(COLS["transfers"], "mean"),
    Avg_Discharges=(COLS["discharges"], "mean"),
    Avg_Transfer_Indicator=("transfer_pct", "mean"),
    Avg_Discharge_Indicator=("discharge_pct", "mean"),
    Records=("Date", "count")
)
order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
weekday_summary["Weekday"] = pd.Categorical(weekday_summary["Weekday"], categories=order, ordered=True)
weekday_summary = weekday_summary.sort_values("Weekday")
fig = px.bar(weekday_summary, x="Weekday", y=["Avg_Transfers","Avg_Discharges"], barmode="group", title="Average daily transfers and discharges by weekday")
st.plotly_chart(fig, use_container_width=True)
with st.expander("View weekday summary"):
    st.dataframe(weekday_summary, use_container_width=True)

st.divider()
st.subheader("5. Threshold alerts")
alerts = []
if latest_valid(view["transfer_pct"]) < transfer_threshold:
    alerts.append(f"Latest transfer indicator is below {transfer_threshold}%.")
if latest_valid(view["discharge_pct"]) < discharge_threshold:
    alerts.append(f"Latest discharge indicator is below {discharge_threshold}%.")
if view["net_pressure"].tail(7).mean() > 0:
    alerts.append("Average intake exceeded discharges across the last 7 selected records.")
if not alerts:
    st.success("No configured threshold alerts for the latest selected record.")
else:
    for msg in alerts:
        st.warning(msg)

st.divider()
st.subheader("6. Data quality and downloadable results")
quality = pd.DataFrame({
    "Field": list(COLS.values()),
    "Missing values": [int(view[c].isna().sum()) for c in COLS.values()],
    "Negative values": [int((view[c] < 0).sum()) for c in COLS.values()],
})
st.dataframe(quality, use_container_width=True)
download = view.to_csv(index=False).encode("utf-8")
st.download_button("Download filtered analysis CSV", download, "care_transition_filtered_analysis.csv", "text/csv")
st.dataframe(view.tail(20).sort_values("Date", ascending=False), use_container_width=True)

st.caption("Interpretation note: Transfer and discharge ratios divide daily flows by same-day reported custody stocks. They are descriptive workload/flow indicators, not true child-level transition probabilities, average time-to-transfer, or sponsor-placement success rates. The dataset does not include individual case IDs, entry/exit timestamps, sponsor type, or case-level duration.")
