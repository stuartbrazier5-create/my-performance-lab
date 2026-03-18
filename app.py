import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# --- APP CONFIG ---
st.set_page_config(page_title="Performance Lab v1.3", layout="wide", page_icon="🚴‍♂️")
st.title("🚀 Performance Lab v1.3")

# --- DATA INGESTION ---
st.sidebar.header("🔗 Data Connection")
CSV_URL = st.sidebar.text_input("Paste Google Sheet CSV Link here:")

if CSV_URL:
    try:
        # 1. Load Data
        df = pd.read_csv(CSV_URL)
        df.columns = df.columns.str.strip() # Remove spaces from headers
        
        # 2. Smart Date Fix (Handles any format)
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date']) # Remove rows with no date
        df = df.sort_values('Date')

        # 3. Handle Empty Metrics (The NaN Fix)
        # We fill empty cells with 0 so the math doesn't crash
        df['TP_TSS'] = pd.to_numeric(df['TP_TSS'], errors='coerce').fillna(0)
        df['Garmin_HRV'] = pd.to_numeric(df['Garmin_HRV'], errors='coerce').fillna(0)
        df['Garmin_Body_Battery'] = pd.to_numeric(df['Garmin_Body_Battery'], errors='coerce').fillna(0)

        # 4. Vekta-Style Load Modeling
        if len(df) > 0:
            df['Load_8'] = df['TP_TSS'].ewm(span=56).mean()
            df['Load_2'] = df['TP_TSS'].ewm(span=14).mean()
            df['Strain'] = df['Load_2'] - df['Load_8']
            
            # --- SIDEBAR METRICS ---
            latest = df.iloc[-1]
            st.sidebar.subheader("Latest Readings")
            
            # Safe display logic to avoid the 'NaN to Integer' error
            hrv_val = int(latest['Garmin_HRV']) if latest['Garmin_HRV'] > 0 else "N/A"
            bb_val = int(latest['Garmin_Body_Battery']) if latest['Garmin_Body_Battery'] > 0 else "N/A"
            
            st.sidebar.metric("Latest HRV", f"{hrv_val} ms")
            st.sidebar.metric("Body Battery", f"{bb_val}/100")

            # --- TABS ---
            tab1, tab2 = st.tabs(["📈 Readiness & Load", "🛡️ Durability Engine"])
            
            with tab1:
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Volume Trend (Load-8)")
                    fig_load = px.line(df, x='Date', y=['Load_8', 'Load_2'],
                                      color_discrete_map={"Load_8": "blue", "Load_2": "red"})
                    st.plotly_chart(fig_load, use_container_width=True)
                with col2:
                    st.subheader("Daily Training Strain")
                    fig_strain = px.bar(df, x='Date', y='Strain', color='Strain', 
                                       color_continuous_scale='RdYlGn_r')
                    st.plotly_chart(fig_strain, use_container_width=True)

            with tab2:
                st.header("🏁 175km Durability Predictor")
                kj_work = st.slider("Select Accumulated Work (kJ)", 0, 4000, 2000, step=500)
                deg_factor = 1 - (kj_work / 25000) 
                st.metric(f"Predicted CP @ {kj_work}kJ", f"{int(289 * deg_factor)} W")
                st.progress(deg_factor)
        else:
            st.warning("Your sheet is connected, but no data rows were found below the headers.")

    except Exception as e:
        st.error(f"⚠️ Error: {e}")
        st.info("Check that your headers match: Date, Garmin_HRV, Garmin_Body_Battery, TP_TSS, Feel_Score")
else:
    st.info("👋 Paste your CSV link in the sidebar to sync your data.")
