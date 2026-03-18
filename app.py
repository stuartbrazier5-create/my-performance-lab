import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import base64
from datetime import datetime

# --- APP CONFIG ---
st.set_page_config(page_title="Performance Lab v1.6.2", layout="wide", page_icon="⚡")
st.title("🚀 Performance Lab v1.6.2")

# --- SIDEBAR: LINKS & COUNTDOWN ---
st.sidebar.header("🗓️ Race Countdown")
# Setting April 12, 2026 as a placeholder for your April trip
race_date = datetime(2026, 4, 12) 
days_to_race = (race_date - datetime.now()).days
st.sidebar.metric("Days to Barcelona", f"{days_to_race} Days")

st.sidebar.markdown("---")
st.sidebar.header("🔗 Data Connection")
CSV_URL = st.sidebar.text_input("Paste Google Sheet CSV Link here:")

st.sidebar.subheader("🛠️ External Tools")
# FIXED LINK: This is the verified Vekta CP Calculator URL
st.sidebar.link_button("Vekta CP Calculator", "https://vekta-cp-calculator.streamlit.app/")

if CSV_URL:
    try:
        # 1. LOAD & CLEAN
        df = pd.read_csv(CSV_URL)
        df.columns = df.columns.str.strip() 
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date', 'Garmin_HRV']).reset_index(drop=True)
        df = df.sort_values('Date')

        if not df.empty:
            # 2. READINESS MATH
            df['TP_TSS'] = pd.to_numeric(df['TP_TSS'], errors='coerce').fillna(0)
            df['Garmin_HRV'] = pd.to_numeric(df['Garmin_HRV'], errors='coerce').fillna(0)
            df['Garmin_Body_Battery'] = pd.to_numeric(df['Garmin_Body_Battery'], errors='coerce').fillna(0)
            
            hrv_baseline = df['Garmin_HRV'].mean()
            latest = df.iloc[-1]
            hrv_diff = ((latest['Garmin_HRV'] - hrv_baseline) / hrv_baseline) * 100 if hrv_baseline > 0 else 0

            # 3. SIDEBAR STATUS
            st.sidebar.subheader("🛡️ Readiness Status")
            if hrv_diff < -15: st.sidebar.error(f"CRITICAL: HRV {int(hrv_diff)}% down.")
            elif hrv_diff < -5: st.sidebar.warning(f"STRETCHED: HRV {int(hrv_diff)}% down.")
            else: st.sidebar.success(f"OPTIMAL: HRV +{int(hrv_diff)}% vs baseline.")

            st.sidebar.metric("Latest HRV", f"{int(latest['Garmin_HRV'])} ms", delta=f"{int(hrv_diff)}%")
            
            # 4. TABS
            tab1, tab2, tab3, tab4 = st.tabs(["📈 Readiness", "🛡️ Durability", "🍎 Nutrition", "🎮 Workout Architect"])
            
            with tab1:
                df['Load_8'] = df['TP_TSS'].ewm(span=56).mean()
                df['Load_2'] = df['TP_TSS'].ewm(span=14).mean()
                df['Strain'] = df['Load_2'] - df['Load_8']
                
                c1, c2 = st.columns(2)
                with c1:
                    st.subheader("Volume Trend (Load-8)")
                    st.plotly_chart(px.line(df, x='Date', y=['Load_8', 'Load_2'], 
                                   color_discrete_map={"Load_8": "blue", "Load_2": "red"}), use_container_width=True)
                with c2:
                    st.subheader("Daily Training Strain")
                    st.plotly_chart(px.bar(df, x='Date', y='Strain', color='Strain', 
                                   color_continuous_scale='RdYlGn_r'), use_container_width=True)

            with tab2:
                st.header("🏁 175km Durability Engine")
                kj_work = st.slider("Select Accumulated Work (kJ)", 0, 4000, 2000, step=500)
                deg_factor = 1 - (kj_work / 25000) 
                st.metric(f"Predicted CP @ {kj_work}kJ", f"{int(289 * deg_factor)} W", delta=f"-{int(289 - (289 * deg_factor))}W")
                st.progress(deg_factor)

            with tab3:
                st.header("🥤 175km Fueling Strategist")
                t_time = st.slider("Target Finish Time (Hours)", 5.0, 12.0, 7.0, step=0.5)
                c_intensity = st.select_slider("Intensity Target", options=["Low (60g/hr)", "Moderate (80g/hr)", "High (100g/hr)", "Elite (120g/hr)"], value="Moderate (80g/hr)")
                g_hr = int(c_intensity.split('(')[1].split('g')[0])
                st.columns(3)[0].metric("Total Carbs", f"{int(g_hr * t_time)}g")
                st.columns(3)[1].metric("Per Hour", f"{g_hr}g")
                st.columns(3)[2].metric("Est. Bottles", f"{int(t_time * 1.2)}")

            with tab4:
                st.header("🎮 Zwift Workout Architect")
                d_mins = st.number_input("Duration (Minutes)", 30, 300, 90)
                t_pct = st.slider("Intensity (% of CP)", 50, 110, 70)
                zwo = f"""<workout_file><author>Lab</author><name>{d_mins}m @ {t_pct}%</name><workout><Warmup Duration="600" PowerLow="0.45" PowerHigh="0.65"/><SteadyState Duration="{(d_mins-15)*60}" Power="{t_pct/100}"/><Cooldown Duration="300" PowerLow="0.65" PowerHigh="0.45"/></workout></workout_file>"""
                b64 = base64.b64encode(zwo.encode()).decode()
                st.markdown(f'<a href="data:file/xml;base64,{b64}" download="Lab_Ride.zwo">📥 Download Zwift (.zwo) File</a>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"⚠️ Error: {e}")
else:
    st.info("👋 Paste your CSV link to restore graphs and unlock the countdown.")
