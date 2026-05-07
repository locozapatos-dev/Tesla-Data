import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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
    background-size: 55px 55px;
}

h1, h2, h3 {
    font-family: 'Orbitron', sans-serif !important;
    color: #ff2200 !important;
    text-shadow: 0 0 10px rgba(255,34,0,0.6);
    letter-spacing: 0.1em;
}

p, div, span, label {
    font-family: 'JetBrains Mono', monospace !important;
    color: #ff6644 !important;
}

.stMetric {
    background: rgba(255,34,0,0.05);
    border: 1px solid rgba(255,34,0,0.3);
    border-radius: 4px;
    padding: 12px;
}

.stMetric label {
    color: #ff4422 !important;
    font-size: 0.7em !important;
    letter-spacing: 0.15em;
}

.stMetric [data-testid="metric-container"] > div:nth-child(2) {
    color: #ffffff !important;
    font-family: 'Orbitron', sans-serif !important;
}

[data-testid="stHeader"] { background: transparent; }

.block-container { padding-top: 2rem; }

hr { border-color: rgba(255,34,0,0.3); }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# DATA LOAD
# ---------------------------------------------------------
@st.cache_data
def load_data():
    battery  = pd.read_csv("battery_states.csv",  parse_dates=["Timestamp (UTC)"])
    charging = pd.read_csv("charging_states.csv", parse_dates=["Timestamp (UTC)"])
    driving  = pd.read_csv("driving_states.csv",  parse_dates=["Timestamp (UTC)"])
    climate  = pd.read_csv("climate_states.csv",  parse_dates=["Timestamp (UTC)"])
    vehicle  = pd.read_csv("vehicle_states.csv",  parse_dates=["Timestamp (UTC)"])

    tpms_fl  = pd.read_csv("tpms_pressure_fl.csv", parse_dates=["Timestamp (UTC)"])
    tpms_fr  = pd.read_csv("tpms_pressure_fr.csv", parse_dates=["Timestamp (UTC)"])
    tpms_rl  = pd.read_csv("tpms_pressure_rl.csv", parse_dates=["Timestamp (UTC)"])
    tpms_rr  = pd.read_csv("tpms_pressure_rr.csv", parse_dates=["Timestamp (UTC)"])

    tpms = tpms_fl.merge(tpms_fr, on="Timestamp (UTC)", how="outer") \
                  .merge(tpms_rl, on="Timestamp (UTC)", how="outer") \
                  .merge(tpms_rr, on="Timestamp (UTC)", how="outer") \
                  .sort_values("Timestamp (UTC)")

    return battery, charging, driving, climate, vehicle, tpms

battery, charging, driving, climate, vehicle, tpms = load_data()

# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------
st.markdown("# RED_GRID // TESLA_OS")
st.markdown("---")

# ---------------------------------------------------------
# KPI ROW
# ---------------------------------------------------------
latest_bat  = battery.iloc[-1]
latest_chg  = charging.iloc[-1]
latest_drv  = driving.iloc[-1]
latest_clim = climate.iloc[-1]

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "BATTERY RANGE",
        f"{float(latest_chg['Battery Range (mi)']):.1f} mi"
    )
with col2:
    st.metric(
        "CHARGE LEVEL",
        f"{int(latest_chg['Usable Battery Level (%)'])}%"
    )
with col3:
    st.metric(
        "ENERGY REMAINING",
        f"{float(latest_bat['Energy Remaining (kWh)']):.1f} kWh"
    )
with col4:
    st.metric(
        "ODOMETER",
        f"{float(latest_drv['Odometer (mi)']):.1f} mi"
    )
with col5:
    inside_c  = float(latest_clim["Inside Temp (°C)"])
    outside_c = float(latest_clim["Outside Temp (°C)"])
    inside_f  = inside_c  * 9/5 + 32
    outside_f = outside_c * 9/5 + 32
    st.metric(
        "CABIN / OUTSIDE",
        f"{inside_f:.0f}°F / {outside_f:.0f}°F"
    )

st.markdown("---")

# ---------------------------------------------------------
# ROW 1: Energy + Charge Level Over Time
# ---------------------------------------------------------
col_a, col_b = st.columns(2)

with col_a:
    st.markdown("### ENERGY REMAINING")
    fig = px.area(
        battery.dropna(subset=["Energy Remaining (kWh)"]),
        x="Timestamp (UTC)",
        y="Energy Remaining (kWh)",
        color_discrete_sequence=["#ff2200"],
    )
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#ff6644",
        xaxis=dict(gridcolor="rgba(255,34,0,0.15)", title=""),
        yaxis=dict(gridcolor="rgba(255,34,0,0.15)"),
        margin=dict(l=0, r=0, t=10, b=0),
    )
    fig.update_traces(fillcolor="rgba(255,34,0,0.15)", line_width=2)
    st.plotly_chart(fig, use_container_width=True)

with col_b:
    st.markdown("### USABLE BATTERY LEVEL")
    chg_clean = charging.dropna(subset=["Usable Battery Level (%)"])
    fig2 = px.line(
        chg_clean,
        x="Timestamp (UTC)",
        y="Usable Battery Level (%)",
        color_discrete_sequence=["#ff6600"],
    )
    fig2.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#ff6644",
        xaxis=dict(gridcolor="rgba(255,34,0,0.15)", title=""),
        yaxis=dict(gridcolor="rgba(255,34,0,0.15)", range=[0, 100]),
        margin=dict(l=0, r=0, t=10, b=0),
    )
    fig2.update_traces(line_width=2)
    st.plotly_chart(fig2, use_container_width=True)

# ---------------------------------------------------------
# ROW 2: Speed + Cabin Temp
# ---------------------------------------------------------
col_c, col_d = st.columns(2)

with col_c:
    st.markdown("### SPEED")
    drv_clean = driving.dropna(subset=["Speed (mph)"])
    fig3 = px.line(
        drv_clean,
        x="Timestamp (UTC)",
        y="Speed (mph)",
        color_discrete_sequence=["#ff0044"],
    )
    fig3.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#ff6644",
        xaxis=dict(gridcolor="rgba(255,34,0,0.15)", title=""),
        yaxis=dict(gridcolor="rgba(255,34,0,0.15)"),
        margin=dict(l=0, r=0, t=10, b=0),
    )
    fig3.update_traces(line_width=2)
    st.plotly_chart(fig3, use_container_width=True)

with col_d:
    st.markdown("### CABIN vs OUTSIDE TEMP (°F)")
    clim = climate.copy()
    clim["Inside Temp (°F)"]  = clim["Inside Temp (°C)"]  * 9/5 + 32
    clim["Outside Temp (°F)"] = clim["Outside Temp (°C)"] * 9/5 + 32
    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(
        x=clim["Timestamp (UTC)"], y=clim["Inside Temp (°F)"],
        name="Inside", line=dict(color="#ff2200", width=2)
    ))
    fig4.add_trace(go.Scatter(
        x=clim["Timestamp (UTC)"], y=clim["Outside Temp (°F)"],
        name="Outside", line=dict(color="#ff8800", width=2, dash="dot")
    ))
    fig4.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#ff6644",
        xaxis=dict(gridcolor="rgba(255,34,0,0.15)", title=""),
        yaxis=dict(gridcolor="rgba(255,34,0,0.15)"),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#ff6644")),
        margin=dict(l=0, r=0, t=10, b=0),
    )
    st.plotly_chart(fig4, use_container_width=True)

# ---------------------------------------------------------
# ROW 3: Tire Pressure + Charging State Breakdown
# ---------------------------------------------------------
col_e, col_f = st.columns(2)

with col_e:
    st.markdown("### TIRE PRESSURE (BAR)")
    fig5 = go.Figure()
    colors = {"Front Left": "#ff2200", "Front Right": "#ff6600",
              "Rear Left": "#ff0066", "Rear Right": "#ff8800"}
    col_map = {
        "Front Left":  "Front Left Tire Pressure (Bar)",
        "Front Right": "Front Right Tire Pressure (Bar)",
        "Rear Left":   "Rear Left Tire Pressure (Bar)",
        "Rear Right":  "Rear Right Tire Pressure (Bar)",
    }
    for label, col in col_map.items():
        if col in tpms.columns:
            t = tpms.dropna(subset=[col])
            fig5.add_trace(go.Scatter(
                x=t["Timestamp (UTC)"], y=t[col],
                name=label, mode="lines+markers",
                line=dict(color=colors[label], width=2),
                marker=dict(size=6)
            ))
    fig5.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#ff6644",
        xaxis=dict(gridcolor="rgba(255,34,0,0.15)", title=""),
        yaxis=dict(gridcolor="rgba(255,34,0,0.15)"),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#ff6644")),
        margin=dict(l=0, r=0, t=10, b=0),
    )
    st.plotly_chart(fig5, use_container_width=True)

with col_f:
    st.markdown("### CHARGING STATE BREAKDOWN")
    state_counts = charging["Charging State"].value_counts().reset_index()
    state_counts.columns = ["State", "Count"]
    fig6 = px.pie(
        state_counts, names="State", values="Count",
        color_discrete_sequence=["#ff2200", "#ff6600", "#ff0044", "#ff8800"],
        hole=0.5,
    )
    fig6.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#ff6644",
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#ff6644")),
        margin=dict(l=0, r=0, t=10, b=0),
    )
    fig6.update_traces(textfont_color="#ffffff")
    st.plotly_chart(fig6, use_container_width=True)

# ---------------------------------------------------------
# ROW 4: Lifetime Energy + Sentry/Lock Status
# ---------------------------------------------------------
col_g, col_h = st.columns(2)

with col_g:
    st.markdown("### LIFETIME ENERGY USED (kWh)")
    bat_clean = battery.dropna(subset=["Lifetime Energy Used (kWh)"])
    fig7 = px.line(
        bat_clean,
        x="Timestamp (UTC)",
        y="Lifetime Energy Used (kWh)",
        color_discrete_sequence=["#ff2200"],
    )
    fig7.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#ff6644",
        xaxis=dict(gridcolor="rgba(255,34,0,0.15)", title=""),
        yaxis=dict(gridcolor="rgba(255,34,0,0.15)"),
        margin=dict(l=0, r=0, t=10, b=0),
    )
    fig7.update_traces(line_width=2)
    st.plotly_chart(fig7, use_container_width=True)

with col_h:
    st.markdown("### VEHICLE STATUS")
    locked      = bool(int(vehicle["Locked"].iloc[-1]))
    sentry      = bool(int(vehicle["Sentry Mode"].iloc[-1]))
    charge_state = latest_chg["Charging State"]
    shift_state  = latest_drv["Shift State"]

    s1, s2 = st.columns(2)
    with s1:
        st.metric("LOCKED",       "YES" if locked  else "NO")
        st.metric("SENTRY MODE",  "ON"  if sentry  else "OFF")
    with s2:
        st.metric("CHARGING STATE", str(charge_state))
        st.metric("SHIFT STATE",    str(shift_state))

st.markdown("---")
st.markdown(
    "<p style='text-align:center;font-size:0.7em;color:rgba(255,80,50,0.4);'>"
    "RED_GRID // TESLA_OS // TELEMETRY LIVE"
    "</p>",
    unsafe_allow_html=True
)
