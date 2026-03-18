import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import base64
from datetime import datetime

# --- APP CONFIG ---
st.set_page_config(page_title="Performance Lab v1.7", layout="wide", page_icon="⚡")
st.title("🚀 Performance Lab v1.7")

# --- SIDEBAR (Remains consistent with v1.6.3...)
st.sidebar.header("🗓️ Race Countdown")
race_date = datetime(2026, 4, 12) 
st.sidebar.metric("Days to Barcelona", f"{(race_date - datetime.now()).days} Days")
st.sidebar.markdown("---")
CSV_URL = st.sidebar.text_input("Paste Google Sheet CSV Link here:")

if CSV_URL:
    try:
        df = pd.read_csv(CSV_URL)
        df.columns = df.columns.str.strip() 
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date', 'Garmin_HRV']).reset_index(drop=True)
        
        if not df.empty:
            tab1, tab2, tab3, tab4 = st.tabs(["📈 Readiness", "🛡️ Durability", "🍎 Nutrition", "🎮 Workout Architect PRO"])
            
            # (Note: Code for Tabs 1, 2, 3 remains same as previous versions)

            with tab4:
                st.header("🎮 Workout Architect PRO")
                st.write("Design your intervals. No subscription required.")
                
                # 1. Warmup Settings
                w_mins = st.number_input("Warmup (Mins)", 5, 30, 10)
                
                # 2. Main Set (Intervals)
                st.divider()
                st.subheader("Main Set Logic")
                colA, colB, colC = st.columns(3)
                reps = colA.number_input("Reps", 1, 20, 5)
                on_time = colB.number_input("Work Duration (Secs)", 30, 600, 60)
                on_power = colC.number_input("Work Power (% CP)", 80, 150, 110)
                
                colD, colE = st.columns(2)
                off_time = colD.number_input("Rest Duration (Secs)", 30, 600, 60)
                off_power = colE.number_input("Rest Power (% CP)", 40, 70, 55)

                # 3. ZWO Generation Engine
                # Warmup
                intervals_xml = f'<Warmup Duration="{w_mins*60}" PowerLow="0.45" PowerHigh="0.75"/>'
                # Main Set
                for i in range(reps):
                    intervals_xml += f'\n<SteadyState Duration="{on_time}" Power="{on_power/100}"/>'
                    intervals_xml += f'\n<SteadyState Duration="{off_time}" Power="{off_power/100}"/>'
                # Cooldown
                intervals_xml += '\n<Cooldown Duration="300" PowerLow="0.75" PowerHigh="0.45"/>'

                zwo = f"""<workout_file><author>Lab</author><name>{reps}x{on_time}s Intervals</name><description>Custom Pro Build.</description><sportType>bike</sportType><workout>{intervals_xml}</workout></workout_file>"""
                
                # Download Button
                b64 = base64.b64encode(zwo.encode()).decode()
                st.markdown(f'<a href="data:file/xml;base64,{b64}" download="Custom_Intervals.zwo" style="padding: 20px; background-color: #ff4b4b; color: white; text-decoration: none; border-radius: 10px;">📥 DOWNLOAD YOUR WORKOUT</a>', unsafe_allow_html=True)
                
                st.info("The .ZWO file will automatically use your FTP/CP settings once loaded into Zwift.")

    except Exception as e:
        st.error(f"⚠️ Error: {e}")
