import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="RED_GRID // TESLA_OS",
    page_icon="🔴",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------
# TESLA x TRON UI
# ---------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=JetBrains+Mono:wght@300&display=swap');

.stApp {
    background-color: #050000;
    background-image:
        linear-gradient(0deg, transparent 24%, rgba(255,0,0,.05) 25%, rgba(255,0,0,.05) 26%, transparent 27%, transparent 74%, rgba(255,0,0,.05) 75%, rgba(255,0,0,.05) 76%, transparent 77%),
        linear-gradient(90deg, transparent 24%, rgba(255,0,0,.05) 25%, rgba(255,0,0,.05) 26%, transparent 27%, transparent 74%, rgba(255,0,0,.05) 75%, rgba(255,0,0,.05) 76%, transparent 77%);
    background-size: 50px 50px;
}

/* Headers */
h1, h2, h3 {
    font-family: 'Orbitron', sans-serif !important;
    color: #ff0000 !important;
    text-shadow: 0 0 15px rgba(255,0,0,0.7);
    letter-spacing: 6px;
}

/* Metrics */
[data-testid="stMetric"] {
    background: rgba(20,0,0,0.85);
    border: 1px solid #ff0000;
    box-shadow: 0 0 10px rgba(255,0,0,0.3), inset 0 0 5px rgba(255,0,0,0.2);
    padding: 16px;
    border-radius: 2px;
}

[data-testid="stMetricValue"] {
    font-family: 'Orbitron';
    color: #ff0000;
    text-shadow: 0 0 8px rgba(255,0,0,0.8);
}

/* Inputs */
label {
    color: #ff0000 !important;
    font-family: 'JetBrains Mono';
    letter-spacing: 2px;
    text-transform: uppercase;
}

hr {
    border: none;
    height: 1px;
    background: linear-gradient(to right, transparent, red, transparent);
}

header, footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------
@st.cache_data
def load_data():
    files = {
        "bat": "battery_states.csv",
        "chg": "charging_states.csv",
        "cli": "climate_states.csv",
        "drv": "driving_states.csv",
        "veh": "vehicle_states.csv"
    }

    data = {}
    for key, path in files.items():
        try:
            df = pd.read_csv(path, encoding="latin-1")
            df.columns = df.columns.str.replace('Â', '', regex=False)

            if "Timestamp (UTC)" in df.columns:
                df["Timestamp (UTC)"] = pd.to_datetime(df["Timestamp (UTC)"], errors="coerce")
                df = df.dropna(subset=["Timestamp (UTC)"]).sort_values("Timestamp (UTC)")

            data[key] = df
        except:
            data[key] = pd.DataFrame()

    return data

data = load_data()

# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------
st.markdown("""
<div style="border-left:4px solid red;padding-left:15px;margin-bottom:20px;">
<h1>TESLA // RED_GRID OS</h1>
<p style="font-family:JetBrains Mono;color:#ff5555;">USER: DRIVER // STATUS: CONNECTED</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# TIME CONTROL
# ---------------------------------------------------------
view = st.select_slider(
    "SCAN RESOLUTION",
    ["5 Min", "Hourly", "Daily", "Weekly", "Monthly"],
    value="Hourly"
)

# ---------------------------------------------------------
# RESAMPLING
# ---------------------------------------------------------
def resample_df(df, view):
    if df.empty or view == "5 Min":
        return df

    if "Timestamp (UTC)" not in df.columns:
        return df

    df = df.copy().set_index("Timestamp (UTC)")

    freq_map = {
        "Hourly": "h",
        "Daily": "d",
        "Weekly": "w",
        "Monthly": "ME"
    }

    freq = freq_map.get(view, "h")

    numeric = df.select_dtypes(include="number")
    if numeric.empty:
        return df.reset_index()

    res = numeric.resample(freq).mean().interpolate(limit_direction="both")
    return res.reset_index()

bat_r = resample_df(data["bat"], view)
chg_r = resample_df(data["chg"], view)
cli_r = resample_df(data["cli"], view)
drv_r = resample_df(data["drv"], view)

# ---------------------------------------------------------
# SAFE VALUE
# ---------------------------------------------------------
def safe_val(df, col, suffix=""):
    if df.empty or col not in df.columns:
        return "--"
    v = df[col].iloc[-1]
    if isinstance(v, (int, float)):
        return f"{v:.1f}{suffix}"
    return str(v)

# ---------------------------------------------------------
# KPIs
# ---------------------------------------------------------
c1, c2, c3, c4 = st.columns(4)

c1.metric("BATTERY", safe_val(data["chg"], "Usable Battery Level (%)", "%"))
c2.metric("RANGE", safe_val(data["chg"], "Battery Range (mi)", " mi"))
c3.metric("SPEED", safe_val(data["drv"], "Speed (mph)", " mph"))
c4.metric("STATE", safe_val(data["chg"], "Charging State"))

st.write("---")

# ---------------------------------------------------------
# CHART STYLE
# ---------------------------------------------------------
def style(fig, color="#ff0000"):
    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=30, b=0),
        hovermode="x unified"
    )
    fig.update_traces(
        line=dict(width=3, color=color, shape="spline"),
        fill="tozeroy",
        fillcolor="rgba(255,0,0,0.12)"
    )
    return fig

def safe_plot(df, y_cols, color, title):
    cols = [c for c in y_cols if c in df.columns]
    if df.empty or not cols:
        st.warning(f"No data for {title}")
        return
    fig = px.line(df, x="Timestamp (UTC)", y=cols)
    st.plotly_chart(style(fig, color), use_container_width=True)

# ---------------------------------------------------------
# VISUALS
# ---------------------------------------------------------
st.markdown("### ⏻ POWER CORE")
safe_plot(bat_r, ["Energy Remaining (kWh)"], "#ff0000", "Battery")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### ➤ VELOCITY VECTOR")
    safe_plot(drv_r, ["Speed (mph)"], "#ff8800", "Speed")

with col2:
    st.markdown("### ◉ THERMAL SYSTEM")
    safe_plot(cli_r, ["Inside Temp (°C)", "Outside Temp (°C)"], "#ff4444", "Temp")

# ---------------------------------------------------------
# DRIVE LOG
# ---------------------------------------------------------
st.markdown("### ◎ DRIVE LOG")

drv_raw = data["drv"]
if not drv_raw.empty and "Speed (mph)" in drv_raw.columns:
    df = drv_raw.copy()
    df["moving"] = df["Speed (mph)"] > 5
    df["trip"] = (df["moving"] != df["moving"].shift()).cumsum()

    trips = (
        df[df["moving"]]
        .groupby("trip")
        .agg(
            start=("Timestamp (UTC)", "min"),
            end=("Timestamp (UTC)", "max"),
            max_speed=("Speed (mph)", "max"),
            avg_speed=("Speed (mph)", "mean")
        )
        .reset_index(drop=True)
    )

    if not trips.empty:
        st.dataframe(trips.tail(10))
    else:
        st.info("No driving sessions detected")

# ---------------------------------------------------------
# CHARGING
# ---------------------------------------------------------
st.markdown("### ⏼ CHARGING SESSIONS")

chg_raw = data["chg"]
if not chg_raw.empty and "Charging State" in chg_raw.columns:
    df = chg_raw.copy()
    df["charging"] = df["Charging State"].astype(str).str.contains("Charging", na=False)
    df["session"] = (df["charging"] != df["charging"].shift()).cumsum()

    sessions = (
        df[df["charging"]]
        .groupby("session")
        .agg(
            start=("Timestamp (UTC)", "min"),
            end=("Timestamp (UTC)", "max"),
            avg_power=("Charger Power (kW)", "mean")
        )
        .reset_index(drop=True)
    )

    if not sessions.empty:
        st.dataframe(sessions.tail(10))
    else:
        st.info("No charging sessions detected")

# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.markdown("""
<div style="text-align:center;margin-top:40px;color:red;">
END OF LINE // SYSTEM ACTIVE
</div>
""", unsafe_allow_html=True)