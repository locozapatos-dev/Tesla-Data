# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

A Streamlit dashboard ("RED_GRID // TESLA_OS") that visualizes Tesla vehicle telemetry data exported from TeslaMate or a similar logger. The single-page app reads CSV files and renders real-time-style charts with a dark red/Tron aesthetic.

## Running the app

```bash
pip install -r requirements.txt
python3 -m streamlit run app.py
```

The app runs on `http://localhost:8501` by default. It reads CSVs from the current working directory, so launch from the repo root.

## Data files

All CSVs share a `Timestamp (UTC)` column and are loaded once via `@st.cache_data`. The files and their key columns:

| File | Key columns |
|------|-------------|
| `battery_states.csv` | `Energy Remaining (kWh)`, `Lifetime Energy Used (kWh)` |
| `charging_states.csv` | `Usable Battery Level (%)`, `Battery Range (mi)`, `Charging State` |
| `driving_states.csv` | `Speed (mph)`, `Odometer (mi)`, `Shift State`, `Latitude`, `Longitude` |
| `climate_states.csv` | `Inside Temp (°C)`, `Outside Temp (°C)` |
| `vehicle_states.csv` | `Locked`, `Sentry Mode` |
| `tpms_pressure_{fl,fr,rl,rr}.csv` | `{Front/Rear} {Left/Right} Tire Pressure (Bar)` |

The four TPMS files are merged on `Timestamp (UTC)` (outer join) into a single `tpms` DataFrame inside `load_data()`.

## Architecture

`app.py` is a single-file Streamlit script structured as:
1. **Config** — page setup and CSS injection (Orbitron/JetBrains Mono fonts, dark red grid theme)
2. **`load_data()`** — cached loader; returns 6 DataFrames
3. **KPI row** — 5 `st.metric` widgets using the last row of each DataFrame
4. **Chart rows** — 4 rows × 2 columns of Plotly figures, all using a transparent dark background with `rgba(255,34,0,…)` grid lines

All Plotly charts use the same layout pattern: `plot_bgcolor`/`paper_bgcolor` transparent, `font_color="#ff6644"`, red-toned grid lines. Reuse this pattern when adding new charts.

Temperature values in CSVs are Celsius; display converts to Fahrenheit (`°C * 9/5 + 32`).

## Ignored paths

`7SAYGDEE6TA631674/` and `850/` are raw data export directories excluded from git — do not commit files from these paths.
