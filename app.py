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
        linear-gradient(90deg, transparent 24%, rgba(255,0,0,.05) 25%, rgba(255,0,0,.05)