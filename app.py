import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# --- APP CONFIG ---
st.set_page_config(page_title="Performance Lab v1.2", layout="wide", page_icon="🚴‍♂️")
st.title("🚀 Performance Lab v1.2")

# --- DATA INGESTION ---
st.sidebar.header("🔗 Data Connection")
CSV_URL = st.sidebar.text_input("Paste Google Sheet CSV Link here:")

if CSV_URL:
    try:
        df = pd.read_csv(CSV_URL)
        df.columns = df.columns.str.strip()
        
        # Check for required columns
        required_cols = ['Date', 'Garmin_HRV', 'Garmin_Body_Battery', 'TP_TSS', 'Feel_Score']
        missing_cols = [c for c in required_cols if c not in df.columns]
        
        if missing_cols:
            st.error(f"⚠️ Missing Columns: {missing_cols}")
            st.write("Current columns in your sheet:", list(df.columns))
            st.stop()

        # SMART DATE FIX: This handles 3/13/2026 or 13/03/2026 automatically
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date']) # Remove empty date rows
        df = df.sort_values('Date')

        # --- VEKTA-STYLE MODELING ---
        df['Load_8'] = df['TP_TSS'].ewm(span=56).mean()
        df['Load_2'] = df['TP_TSS'].ewm(span=14).mean()
        df['Strain'] = df['Load_2'] - df['Load_8']
        
        # --- SIDEBAR & TABS ---
        latest = df.iloc[-1]
        st.sidebar.metric("Latest HRV", f"{int(latest['Garmin_HRV'])}ms")
        st.sidebar.metric("Body Battery", f"{int(latest['Garmin_Body_Battery'])}/100")
        
        tab1, tab2 = st.tabs(["📈 Readiness & Load", "🛡️ Durability Engine"])
        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Volume Trend (Load-8)")
                fig_load = px.line(df, x='Date', y=['Load_8', 'Load_2'])
                st.plotly_chart(fig_load, use_container_width=True)
            with col2:
                st.subheader("Daily Training Strain")
                fig_strain = px.bar(df, x='Date', y='Strain', color='Strain', color_continuous_scale='RdYlGn_r')
                st.plotly_chart(fig_strain, use_container_width=True)

        with tab2:
            st.header("🏁 175km Durability Predictor")
            kj_work = st.slider("Select Accumulated Work (kJ)", 0, 4000, 2000, step=500)
            deg_factor = 1 - (kj_work / 25000) 
            st.metric(f"Predicted CP @ {kj_work}kJ", f"{int(289 * deg_factor)}W")
            st.progress(deg_factor)

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("👋 Paste your CSV link in the sidebar to sync.")
