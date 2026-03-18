import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# --- APP CONFIG ---
st.set_page_config(page_title="Performance Lab v1.5", layout="wide", page_icon="⚡")
st.title("🚀 Performance Lab v1.5")

# --- DATA INGESTION ---
st.sidebar.header("🔗 Data Connection")
CSV_URL = st.sidebar.text_input("Paste Google Sheet CSV Link here:")

if CSV_URL:
    try:
        df = pd.read_csv(CSV_URL)
        df.columns = df.columns.str.strip() 
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date', 'Garmin_HRV']).reset_index(drop=True)
        df = df.sort_values('Date')

        if not df.empty:
            # 1. DATA PROCESSING
            df['TP_TSS'] = pd.to_numeric(df['TP_TSS'], errors='coerce').fillna(0)
            df['Garmin_HRV'] = pd.to_numeric(df['Garmin_HRV'], errors='coerce').fillna(0)
            df['Garmin_Body_Battery'] = pd.to_numeric(df['Garmin_Body_Battery'], errors='coerce').fillna(0)
            
            # Vekta Load Modeling
            df['Load_8'] = df['TP_TSS'].ewm(span=56).mean()
            df['Load_2'] = df['TP_TSS'].ewm(span=14).mean()
            df['Strain'] = df['Load_2'] - df['Load_8']
            
            # HRV Baseline Calculation (Last 7 days vs 60 days)
            hrv_7d = df['Garmin_HRV'].tail(7).mean()
            hrv_baseline = df['Garmin_HRV'].mean()

            # 2. SIDEBAR: READINESS ALERT
            latest = df.iloc[-1]
            st.sidebar.subheader("🛡️ Readiness Status")
            
            hrv_diff = ((latest['Garmin_HRV'] - hrv_baseline) / hrv_baseline) * 100
            
            if hrv_diff < -15:
                st.sidebar.error(f"READINESS: CRITICAL\nHRV is {int(hrv_diff)}% below baseline. Consider Rest.")
            elif hrv_diff < -5:
                st.sidebar.warning(f"READINESS: STRETCHED\nHRV is {int(hrv_diff)}% below baseline. Stay in Zone 2.")
            else:
                st.sidebar.success(f"READINESS: OPTIMAL\nHRV is {int(hrv_diff)}% vs baseline. All systems GO.")

            st.sidebar.metric("Latest HRV", f"{int(latest['Garmin_HRV'])} ms", delta=f"{int(hrv_diff)}%")
            st.sidebar.metric("Body Battery", f"{int(latest['Garmin_Body_Battery'])}/100")

            # 3. TABS: PERFORMANCE & NUTRITION
            tab1, tab2, tab3 = st.tabs(["📈 Readiness & Load", "🛡️ Durability", "🍎 Nutrition Strategist"])
            
            with tab1:
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Volume Trend (Load-8)")
                    fig_load = px.line(df, x='Date', y=['Load_8', 'Load_2'], color_discrete_map={"Load_8": "blue", "Load_2": "red"})
                    st.plotly_chart(fig_load, use_container_width=True)
                with col2:
                    st.subheader("Daily Training Strain")
                    fig_strain = px.bar(df, x='Date', y='Strain', color='Strain', color_continuous_scale='RdYlGn_r')
                    st.plotly_chart(fig_strain, use_container_width=True)

            with tab2:
                st.header("🏁 175km Durability Engine")
                kj_work = st.slider("Select Accumulated Work (kJ)", 0, 4000, 2000, step=500)
                deg_factor = 1 - (kj_work / 25000) 
                st.metric(f"Predicted CP @ {kj_work}kJ", f"{int(289 * deg_factor)} W", delta=f"-{int(289 - (289 * deg_factor))}W")
                st.progress(deg_factor)

            with tab3:
                st.header("🥤 175km Fueling Strategist")
                target_time = st.slider("Target Finish Time (Hours)", 5
