import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import base64

# --- APP CONFIG ---
st.set_page_config(page_title="Performance Lab v1.6", layout="wide", page_icon="⚡")
st.title("🚀 Performance Lab v1.6")

# --- DATA INGESTION ---
st.sidebar.header("🔗 Data Connection")
CSV_URL = st.sidebar.text_input("Paste Google Sheet CSV Link here:")

# EXTERNAL LINKS
st.sidebar.markdown("---")
st.sidebar.subheader("🛠️ External Tools")
st.sidebar.link_button("Vekta Workout Builder", "https://vektasport.streamlit.app/")

if CSV_URL:
    try:
        df = pd.read_csv(CSV_URL)
        df.columns = df.columns.str.strip() 
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date', 'Garmin_HRV']).reset_index(drop=True)
        df = df.sort_values('Date')

        if not df.empty:
            # 1. READINESS LOGIC
            df['TP_TSS'] = pd.to_numeric(df['TP_TSS'], errors='coerce').fillna(0)
            df['Garmin_HRV'] = pd.to_numeric(df['Garmin_HRV'], errors='coerce').fillna(0)
            hrv_baseline = df['Garmin_HRV'].mean()
            latest = df.iloc[-1]
            hrv_diff = ((latest['Garmin_HRV'] - hrv_baseline) / hrv_baseline) * 100 if hrv_baseline > 0 else 0

            # 2. SIDEBAR STATUS
            st.sidebar.subheader("🛡️ Readiness Status")
            if hrv_diff < -15: st.sidebar.error("READINESS: CRITICAL - Rest Day Recommended")
            elif hrv_diff < -5: st.sidebar.warning("READINESS: STRETCHED - Zone 2 Only")
            else: st.sidebar.success("READINESS: OPTIMAL - High Intensity OK")

            # 3. TABS
            tab1, tab2, tab3, tab4 = st.tabs(["📈 Readiness", "🛡️ Durability", "🍎 Nutrition", "🎮 Workout Architect"])
            
            # (Note: Code for Tab 1, 2, and 3 remains consistent with v1.5.1)

            with tab4:
                st.header("🎮 Zwift Workout Architect")
                st.write("Generate a custom .ZWO file for your next ride based on your CP (289W).")
                
                duration_mins = st.number_input("Duration (Minutes)", 30, 300, 90)
                target_pct = st.slider("Target Intensity (% of CP)", 50, 110, 70)
                
                # ZWO generation logic
                zwo_content = f"""<workout_file>
    <author>Performance Lab</author>
    <name>Generated {duration_mins}m @ {target_pct}%</name>
    <description>Custom session based on readiness.</description>
    <sportType>bike</sportType>
    <workout>
        <Warmup Duration="600" PowerLow="0.45" PowerHigh="0.65"/>
        <SteadyState Duration="{ (duration_mins-15)*60 }" Power="{ target_pct/100 }"/>
        <Cooldown Duration="300" PowerLow="0.65" PowerHigh="0.45"/>
    </workout>
</workout_file>"""
                
                b64 = base64.b64encode(zwo_content.encode()).decode()
                href = f'<a href="data:file/xml;base64,{b64}" download="PerformanceLab_Ride.zwo">📥 Download Zwift (.zwo) File</a>'
                st.markdown(href, unsafe_allow_html=True)
                st.info("Download and drop into: \Documents\Zwift\Workouts\[YourID]")

    except Exception as e:
        st.error(f"⚠️ Error: {e}")
