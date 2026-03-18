import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import base64
from datetime import datetime

# --- APP CONFIG ---
st.set_page_config(page_title="Performance Lab v1.8", layout="wide", page_icon="⚡")
st.title("🚀 Performance Lab v1.8")

# --- SIDEBAR: LINKS & COUNTDOWN ---
st.sidebar.header("🗓️ Race Countdown")
race_date = datetime(2026, 4, 12) 
days_to_race = (race_date - datetime.now()).days
st.sidebar.metric("Days to Barcelona", f"{max(0, days_to_race)} Days")

st.sidebar.markdown("---")
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
            # Metrics & Processing (Standard v1.7 logic)
            df['TP_TSS'] = pd.to_numeric(df['TP_TSS'], errors='coerce').fillna(0)
            df['Garmin_HRV'] = pd.to_numeric(df['Garmin_HRV'], errors='coerce').fillna(0)
            hrv_baseline = df['Garmin_HRV'].mean()
            latest = df.iloc[-1]
            hrv_diff = ((latest['Garmin_HRV'] - hrv_baseline) / hrv_baseline) * 100 if hrv_baseline > 0 else 0

            # TAB DEFINITION
            tab1, tab2, tab3, tab4 = st.tabs(["📈 Readiness", "🛡️ Durability", "🍎 Nutrition", "🎮 Workout Architect PRO"])

            with tab1:
                st.subheader("Volume & Fatigue")
                df['Load_8'] = df['TP_TSS'].ewm(span=56).mean()
                df['Load_2'] = df['TP_TSS'].ewm(span=14).mean()
                df['Strain'] = df['Load_2'] - df['Load_8']
                st.plotly_chart(px.line(df, x='Date', y=['Load_8', 'Load_2']), use_container_width=True)

            with tab2:
                st.header("🏁 Durability Engine")
                # (Standard v1.7 logic...)

            with tab3:
                st.header("🥤 Fueling Strategist")
                # (Standard v1.7 logic...)

            with tab4:
                st.header("🎮 Workout Architect PRO")
                st.info("Interval units are now in **Minutes** for better precision.")

                with st.container(border=True):
                    # 1. Warmup
                    w_mins = st.number_input("Warmup Duration (Mins)", 5, 30, 10)
                    
                    st.markdown("### Main Set Logic")
                    colA, colB, colC = st.columns(3)
                    reps = colA.number_input("Reps", 1, 20, 5)
                    on_mins = colB.number_input("Work Duration (Mins)", 0.5, 30.0, 2.0, step=0.5)
                    on_power = colC.number_input("Work Power (% CP)", 80, 150, 110)
                    
                    colD, colE = st.columns(2)
                    off_mins = colD.number_input("Rest Duration (Mins)", 0.5, 30.0, 1.0, step=0.5)
                    off_power = colE.number_input("Rest Power (% CP)", 40, 70, 55)

                # --- VISUAL PREVIEW ---
                st.divider()
                st.subheader("Workout Preview")
                
                # Build dummy data for graph
                time_pts = [0, w_mins]
                power_pts = [45, 75]
                current_time = w_mins
                for _ in range(reps):
                    time_pts.extend([current_time, current_time + on_mins])
                    power_pts.extend([on_power, on_power])
                    current_time += on_mins
                    time_pts.extend([current_time, current_time + off_mins])
                    power_pts.extend([off_power, off_power])
                    current_time += off_mins
                time_pts.extend([current_time, current_time + 5])
                power_pts.extend([75, 45])

                fig = go.Figure()
                fig.add_trace(go.Scatter(x=time_pts, y=power_pts, fill='tozeroy', line_color='red', name='Power %'))
                fig.update_layout(height=300, margin=dict(l=20, r=20, t=20, b=20), xaxis_title="Minutes", yaxis_title="% of CP")
                st.plotly_chart(fig, use_container_width=True)

                # --- ZWO GENERATION ---
                st.markdown("<br>", unsafe_allow_html=True) # Extra Padding
                
                intervals_xml = f'<Warmup Duration="{w_mins*60}" PowerLow="0.45" PowerHigh="0.75"/>'
                for i in range(reps):
                    intervals_xml += f'\n<SteadyState Duration="{int(on_mins*60)}" Power="{on_power/100}"/>'
                    intervals_xml += f'\n<SteadyState Duration="{int(off_mins*60)}" Power="{off_power/100}"/>'
                intervals_xml += '\n<Cooldown Duration="300" PowerLow="0.75" PowerHigh="0.45"/>'

                zwo = f"""<workout_file><author>Lab</author><name>{reps}x{on_mins}m Intervals</name><description>Custom Pro Build.</description><sportType>bike</sportType><workout>{intervals_xml}</workout></workout_file>"""
                
                b64 = base64.b64encode(zwo.encode()).decode()
                st.markdown(f'<a href="data:file/xml;base64,{b64}" download="Workout.zwo" style="display: block; width: 100%; text-align: center; padding: 15px; background-color: #ff4b4b; color: white; border-radius: 10px; font-weight: bold; text-decoration: none;">📥 DOWNLOAD ZWIFT FILE</a>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"⚠️ Error: {e}")
