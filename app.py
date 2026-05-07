# Updated Tesla RED_GRID Dashboard Script (Improved Drive Log + Charging Sessions UI)

```python
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

h1, h2, h3 {
    font-family: 'Orbitron', sans-serif !important;
    color: #ff0000 !important;
    text-shadow: 0 0 15px rgba(255,0,0,0.7);
    letter-spacing: 6px;
}

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

label {
    color: #ff0000 !important;
    font-family: 'JetBrains Mono';
    letter-spacing: 2px;
    text-transform: uppercase;
}

section[data-testid="stSidebar"] {
    display: none;
}

header, footer {
    visibility: hidden;
}

.tron-card {
    background: rgba(15,0,0,0.88);
    border: 1px solid rgba(255,0,0,0.4);
    padding: 18px;
    margin-bottom: 12px;
    box-shadow: 0 0 14px rgba(255,0,0,0.15);
    border-radius: 4px;
}

.tron-title {
    color: #ff4444;
    font-family: Orbitron;
    letter-spacing: 2px;
    font-size: 0.8rem;
}

.tron-value {
    color: #ffffff;
    font-family: 'JetBrains Mono';
    font-size: 1.1rem;
}

.tron-divider {
    height: 1px;
    background: linear-gradient(to right, transparent, red, transparent);
    margin-top: 10px;
    margin-bottom: 10px;
}
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
                df["Timestamp (UTC)"] = pd.to_datetime(
                    df["Timestamp (UTC)"],
                    errors="coerce"
                )
                df = df.dropna(subset=["Timestamp (UTC)"])
                df = df.sort_values("Timestamp (UTC)")

            data[key] = df

        except Exception:
            data[key] = pd.DataFrame()

    return data


data = load_data()

# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------
st.markdown("""
<div style="border-left:4px solid red;padding-left:15px;margin-bottom:20px;">
<h1>TESLA // RED_GRID OS</h1>
<p style="font-family:JetBrains Mono;color:#ff5555;">
USER: DRIVER // STATUS: CONNECTED
</p>
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
# KPI BAR
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
        hovermode="x unified",
        showlegend=False
    )

    fig.update_traces(
        line=dict(width=3, color=color, shape="spline"),
        fill="tozeroy",
        fillcolor="rgba(255,0,0,0.10)"
    )

    return fig

# ---------------------------------------------------------
# SAFE PLOT
# ---------------------------------------------------------
def safe_plot(df, y_cols, color, title):

    cols = [c for c in y_cols if c in df.columns]

    if df.empty or not cols:
        st.warning(f"No data for {title}")
        return

    fig = px.line(
        df,
        x="Timestamp (UTC)",
        y=cols
    )

    st.plotly_chart(
        style(fig, color),
        use_container_width=True
    )

# ---------------------------------------------------------
# MAIN VISUALS
# ---------------------------------------------------------
st.markdown("### ⏻ POWER CORE")
safe_plot(bat_r, ["Energy Remaining (kWh)"], "#ff0000", "Battery")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### ➤ VELOCITY VECTOR")
    safe_plot(drv_r, ["Speed (mph)"], "#ff8800", "Speed")

with col2:
    st.markdown("### ◉ THERMAL SYSTEM")
    safe_plot(
        cli_r,
        ["Inside Temp (°C)", "Outside Temp (°C)"],
        "#ff4444",
        "Thermal"
    )

# ---------------------------------------------------------
# DRIVE LOG REBUILT
# ---------------------------------------------------------
st.markdown("### ◎ DRIVE SESSIONS")

if not data["drv"].empty and "Speed (mph)" in data["drv"].columns:

    drv = data["drv"].copy()

    drv["moving"] = drv["Speed (mph)"] > 5
    drv["trip"] = (drv["moving"] != drv["moving"].shift()).cumsum()

    trips = (
        drv[drv["moving"]]
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

        trips = trips.tail(6).iloc[::-1]

        cols = st.columns(2)

        for i, (_, row) in enumerate(trips.iterrows()):

            duration = row['end'] - row['start']
            mins = int(duration.total_seconds() / 60)

            with cols[i % 2]:

                st.markdown(f"""
                <div class="tron-card">
                    <div class="tron-title">DRIVE SESSION</div>
                    <div class="tron-divider"></div>

                    <div class="tron-title">START</div>
                    <div class="tron-value">{row['start']}</div>

                    <br>

                    <div class="tron-title">END</div>
                    <div class="tron-value">{row['end']}</div>

                    <br>

                    <div class="tron-title">MAX SPEED</div>
                    <div class="tron-value">{row['max_speed']:.1f} MPH</div>

                    <br>

                    <div class="tron-title">AVG SPEED</div>
                    <div class="tron-value">{row['avg_speed']:.1f} MPH</div>

                    <br>

                    <div class="tron-title">DURATION</div>
                    <div class="tron-value">{mins} MINUTES</div>
                </div>
                """, unsafe_allow_html=True)

# ---------------------------------------------------------
# CHARGING UI REBUILT
# ---------------------------------------------------------
st.markdown("### ⏼ CHARGE CYCLES")

if not data["chg"].empty and "Charging State" in data["chg"].columns:

    chg = data["chg"].copy()

    chg["charging"] = chg["Charging State"].astype(str).str.contains(
        "Charging",
        na=False
    )

    chg["session"] = (
        chg["charging"] != chg["charging"].shift()
    ).cumsum()

    sessions = (
        chg[chg["charging"]]
        .groupby("session")
        .agg(
            start=("Timestamp (UTC)", "min"),
            end=("Timestamp (UTC)", "max"),
            avg_power=("Charger Power (kW)", "mean"),
            battery=("Usable Battery Level (%)", "max")
        )
        .reset_index(drop=True)
    )

    if not sessions.empty:

        sessions = sessions.tail(6).iloc[::-1]

        cols = st.columns(2)

        for i, (_, row) in enumerate(sessions.iterrows()):

            duration = row['end'] - row['start']
            mins = int(duration.total_seconds() / 60)

            with cols[i % 2]:

                st.markdown(f"""
                <div class="tron-card">
                    <div class="tron-title">CHARGE SESSION</div>
                    <div class="tron-divider"></div>

                    <div class="tron-title">START</div>
                    <div class="tron-value">{row['start']}</div>

                    <br>

                    <div class="tron-title">END</div>
                    <div class="tron-value">{row['end']}</div>

                    <br>

                    <div class="tron-title">AVG POWER</div>
                    <div class="tron-value">{row['avg_power']:.1f} KW</div>

                    <br>

                    <div class="tron-title">BATTERY LEVEL</div>
                    <div class="tron-value">{row['battery']:.1f}%</div>

                    <br>

                    <div class="tron-title">DURATION</div>
                    <div class="tron-value">{mins} MINUTES</div>
                </div>
                """, unsafe_allow_html=True)

# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.markdown("""
<div style="text-align:center;margin-top:40px;color:red;">
END OF LINE // SYSTEM ACTIVE
</div>
""", unsafe_allow_html=True)
```
