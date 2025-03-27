import streamlit as st
import random
import json
import pandas as pd

# Import our mock API
from api import api

# UI setup
st.set_page_config(
    page_title="Digital Twin Brewing Control",
    page_icon="🍺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state
if "system_status" not in st.session_state:
    st.session_state.system_status = api.get_system_status()

if "refresh_counter" not in st.session_state:
    st.session_state.refresh_counter = 0

# Sidebar
with st.sidebar:
    st.title("Brewing Digital Twin")

    if st.button("Refresh Data"):
        st.session_state.system_status = api.get_system_status()
        st.session_state.refresh_counter += 1

    st.subheader("Control Panel")

    # Data collection frequency slider
    freq = st.slider(
        "Data Collection Frequency (minutes)",
        min_value=1,
        max_value=60,
        value=st.session_state.system_status["data_collection_frequency"],
        step=1,
    )

    if st.button("Update Frequency"):
        result = api.update_data_frequency(freq)
        if result["success"]:
            st.success(result["message"])
            st.session_state.system_status["data_collection_frequency"] = freq
        else:
            st.error(result["message"])

    st.markdown("---")
    st.caption("Last update: " + st.session_state.system_status["last_update"])
    st.caption(f"System state: {st.session_state.system_status['system_state']}")

    if st.session_state.system_status["safe_mode"]:
        st.info("Safety Mode: Active")
    else:
        st.warning("Safety Mode: Inactive")

# Main area
st.title("Brewing System Dashboard")

# Status cards
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Temperature",
        value=f"{st.session_state.system_status['temperature']} °C",
        delta=round(random.uniform(-0.5, 0.5), 1),
    )

with col2:
    pressure_value = st.session_state.system_status["pressure"]
    thresholds = api.get_safety_thresholds()

    if pressure_value > thresholds["max_pressure"] * 0.9:
        st.metric(
            label="Pressure",
            value=f"{pressure_value} bar",
            delta=round(random.uniform(-0.1, 0.1), 2),
            delta_color="inverse",
        )
        st.warning("Approaching max pressure")
    else:
        st.metric(
            label="Pressure",
            value=f"{pressure_value} bar",
            delta=round(random.uniform(-0.1, 0.1), 2),
        )

with col3:
    st.metric(
        label="pH Level",
        value=st.session_state.system_status["ph_level"],
        delta=round(random.uniform(-0.2, 0.2), 1),
    )

with col4:
    st.metric(
        label="Dissolved Oxygen",
        value=f"{st.session_state.system_status['dissolved_oxygen']} mg/L",
        delta=round(random.uniform(-0.5, 0.5), 2),
    )

# Historical data chart
st.subheader("Fermentation History (Last 48 Hours)")
historical_data = api.get_historical_data()

# Create DataFrames with proper structure for charts
chart_tab1, chart_tab2, chart_tab3, chart_tab4 = st.tabs(
    ["Temperature", "Pressure", "pH", "Dissolved Oxygen"]
)

with chart_tab1:
    temp_df = pd.DataFrame(
        {
            "timestamps": historical_data["timestamps"],
            "Temperature (°C)": historical_data["temperature"],
        }
    )
    st.line_chart(temp_df, x="timestamps", y="Temperature (°C)")

with chart_tab2:
    pressure_df = pd.DataFrame(
        {
            "timestamps": historical_data["timestamps"],
            "Pressure (bar)": historical_data["pressure"],
        }
    )
    st.line_chart(pressure_df, x="timestamps", y="Pressure (bar)")

with chart_tab3:
    ph_df = pd.DataFrame(
        {
            "timestamps": historical_data["timestamps"],
            "pH Level": historical_data["ph_level"],
        }
    )
    st.line_chart(ph_df, x="timestamps", y="pH Level")

with chart_tab4:
    oxygen_df = pd.DataFrame(
        {
            "timestamps": historical_data["timestamps"],
            "Dissolved Oxygen (mg/L)": historical_data["dissolved_oxygen"],
        }
    )
    st.line_chart(oxygen_df, x="timestamps", y="Dissolved Oxygen (mg/L)")

# Control section - with safety measures
st.subheader("System Controls")
st.warning("⚠️ Critical operations require physical presence at the brewing site")

control_col1, control_col2 = st.columns(2)

with control_col1:
    st.write("Non-critical Parameters")

    with st.form("non_critical_form"):
        temp_adjustment = st.slider("Temperature Offset (±°C)", -2.0, 2.0, 0.0, 0.1)
        data_notes = st.text_area("Batch Notes", "")
        submitted = st.form_submit_button("Apply Changes")

        if submitted:
            result = api.send_command("set_temp_offset", temp_adjustment)
            if result["success"]:
                st.success("Non-critical parameters updated")
            else:
                st.error(result["message"])

with control_col2:
    st.write("Critical Operations (Require Physical Access)")

    with st.form("critical_form"):
        pressure_set = st.slider("Set Pressure (bar)", 0.5, 3.0, 1.5, 0.1)
        start_new_batch = st.checkbox("Start New Fermentation Batch")
        verification_code = st.text_input("Physical Verification Code", type="password")
        critical_submitted = st.form_submit_button("Send Command")

        if critical_submitted:
            if verification_code:
                if start_new_batch:
                    result = api.send_command("start_batch", "", verification_code)
                else:
                    result = api.send_command(
                        "set_pressure", pressure_set, verification_code
                    )

                if result["success"]:
                    st.success(result["message"])
                else:
                    st.error(result["message"])
            else:
                st.error("Verification code required for critical operations")

# System information
with st.expander("System Information"):
    thresholds = api.get_safety_thresholds()

    st.write("Safety Thresholds:")
    st.json(json.dumps(thresholds, indent=2))

    st.write("Raw System Status:")
    st.json(json.dumps(st.session_state.system_status, indent=2))
