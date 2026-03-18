import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# --- VEKTA MATHEMATICAL ENGINE ---
def calculate_w_prime_balance(power_stream, cp, w_prime, tau=300):
    """Models the 'Anaerobic Battery' using the Vekta exponential reconstitution."""
    w_bal = [w_prime]
    for p in power_stream:
        prev_w = w_bal[-1]
        if p > cp:
            # Depletion is linear
            new_w = prev_w - (p - cp)
        else:
            # Reconstitution is exponential (Vekta Tau Logic)
            new_w = w_prime - (w_prime - prev_w) * np.exp(-1/tau)
        w_bal.append(max(0, new_w))
    return w_bal

# --- APP INTERFACE ---
st.set_page_config(page_title="Athlete Performance Lab", layout="wide")
st.title("🚀 Athlete Performance Lab (APL) v1.0")
st.sidebar.markdown("### 🧬 Vekta Engine Active")

# DATA LINK (Connects to your Google Sheet)
# Replace 'YOUR_SHEET_URL' with your 'Public' Google Sheet CSV link
SHEET_URL = st.sidebar.text_input("Paste Google Sheet CSV Link", "")

if SHEET_URL:
    df = pd.read_csv(SHEET_URL)
    df['Date'] = pd.to_datetime(df['Date'])
    
    # 1. READINESS VIEW (Garmin + TP)
    st.header("1. Readiness & Recovery")
    col1, col2, col3 = st.columns(3)
    latest = df.iloc[-1]
    col1.metric("Garmin HRV", f"{latest['Garmin_HRV']}ms", delta="Balanced")
    col2.metric("Body Battery", f"{latest['Garmin_Body_Battery']}/100")
    col3.metric("Last Session TSS", latest['TP_TSS'])

    # 2. VEKTA LOAD MODELING (Load-8 vs Load-2)
    st.header("2. Volume & Strain (Vekta Modeling)")
    df['Load_8'] = df['TP_TSS'].ewm(span=56).mean() # 8-week Fitness
    df['Load_2'] = df['TP_TSS'].ewm(span=14).mean() # 2-week Fatigue
    df['Strain'] = df['Load_2'] - df['Load_8']
    
    fig_load = px.line(df, x='Date', y=['Load_8', 'Load_2'], 
                      title="Fitness (Load-8) vs. Fatigue (Load-2)")
    st.plotly_chart(fig_load, use_container_width=True)

    # 3. DURABILITY PREDICTOR (175km Race Logic)
    st.header("3. 175km Race Durability")
    st.info("Predicting power degradation after 2,000kJ - 3,000kJ of work.")
    
    cp_fresh = 289 # Your current CP
    kj_work = st.slider("Work Done (kJ)", 0, 4000, 2000)
    
    # Durability Formula derived from Research: 
    # Fatigue Driver = a*(kJ/kg) + b*(Time_above_CP)
    degradation = 1 - (kj_work / 30000) # Simple estimate for v1.0
    cp_fatigued = cp_fresh * degradation
    
    st.write(f"**Predicted CP after {kj_work}kJ:** {cp_fatigued:.1f}W")
    st.progress(degradation)

else:
    st.warning("Please paste your Google Sheet CSV link in the sidebar to begin.")
