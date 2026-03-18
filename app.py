import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# --- APP CONFIG ---
st.set_page_config(page_title="Performance Lab v1.0", layout="wide", page_icon="🚴‍♂️")
st.title("🚀 Performance Lab v1.0")
st.markdown("#### Garmin Readiness + TrainingPeaks Volume + Durability Engine")

# --- DATA INGESTION ---
# Enter your Public CSV Link in the Sidebar
st.sidebar.header("🔗 Data Connection")
CSV_URL = st.sidebar.text_input("Paste Google Sheet CSV Link here:", help="File > Share > Publish to Web > CSV")

if CSV_URL:
    try:
        # Load Data
        df = pd.read_csv(CSV_URL)
        df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)
        df = df.sort_values('Date')

        # --- VEKTA-STYLE MODELING ---
        # Load-8 (Fitness) and Load-2 (Fatigue)
        df['Load_8'] = df['TP_TSS'].ewm(span=56).mean()
        df['Load_2'] = df['TP_TSS'].ewm(span=14).mean()
        df['Strain'] = df['Load_2'] - df['Load_8']
        
        # --- SIDEBAR: LATEST STATUS ---
        latest = df.iloc[-1]
        st.sidebar.metric("Latest HRV", f"{latest['Garmin_HRV']}ms")
        st.sidebar.metric("Body Battery", f"{latest['Garmin_Body_Battery']}/100")
        st.sidebar.metric("Feel Score", f"{latest['Feel_Score']}/10")

        # --- TAB 1: READINESS DASHBOARD ---
        tab1, tab2 = st.tabs(["📈 Readiness & Load", "🛡️ Durability Engine"])
        
        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Volume Trend (Load-8)")
                fig_load = px.line(df, x='Date', y=['Load_8', 'Load_2'], 
                                  color_discrete_map={"Load_8": "blue", "Load_2": "red"},
                                  labels={"value": "TSS", "variable": "Metric"})
                st.plotly_chart(fig_load, use_container_width=True)
            
            with col2:
                st.subheader("Daily Training Strain")
                # Visualizing 'Peaking' - we want Strain to go positive for building, negative for tapering
                fig_strain = px.bar(df, x='Date', y='Strain', color='Strain',
                                   color_continuous_scale='RdYlGn_r')
                st.plotly_chart(fig_strain, use_container_width=True)

        # --- TAB 2: DURABILITY (175km RACE PREDICTOR) ---
        with tab2:
            st.header("🏁 The 175km Durability Predictor")
            st.write("Predicting your Critical Power (CP) degradation based on work done (kJ).")
            
            cp_fresh = 289 # Based on your Zwift FTP
            kj_work = st.slider("Select Accumulated Work (kJ)", 0, 4000, 2000, step=500)
            
            # Durability Math: Degradation is typically 5-15% after 3000kJ for elite-amateurs
            # We will refine this once we have your real file data
            deg_factor = 1 - (kj_work / 25000) 
            cp_fatigued = cp_fresh * deg_factor
            
            c1, c2 = st.columns(2)
            c1.metric("Fresh CP", f"{cp_fresh}W")
            c2.metric(f"Predicted CP @ {kj_work}kJ", f"{int(cp_fatigued)}W", 
                      delta=f"-{int(cp_fresh - cp_fatigued)}W", delta_color="inverse")
            
            st.progress(deg_factor)
            st.caption("Note: This model will become more accurate as you upload your .FIT files.")

    except Exception as e:
        st.error(f"Error loading data: {e}. Ensure your Google Sheet is published as CSV and contains the correct headers.")
else:
    st.info("👋 Welcome! Please paste your 'Published to Web' CSV link in the sidebar to visualize your training data.")
