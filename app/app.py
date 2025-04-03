import streamlit as st
import random
import json
import pandas as pd

# Import our APIs
from api import api, mock_api, real_api

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

if "data_source" not in st.session_state:
    st.session_state.data_source = "mock"

# Function to switch API
def switch_data_source():
    import api as api_module
    if st.session_state.data_source == "mock":
        api_module.api = mock_api
    else:
        api_module.api = real_api
    
    # Update system status with new API
    st.session_state.system_status = api_module.api.get_system_status()

# Sidebar
with st.sidebar:
    st.title("Brewing Digital Twin")
    
    # Data source selection
    st.subheader("Data Source")
    data_source = st.radio(
        "Select data source",
        options=["mock", "real"],
        index=0 if st.session_state.data_source == "mock" else 1,
        key="data_source",
        on_change=switch_data_source,
        help="Switch between mock data and real API data"
    )

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

# Check if we have real data or not
no_data = st.session_state.system_status.get('no_data_available', False)

if no_data:
    with st.container():
        st.warning("⚠️ No data available from the fermentation prototype. Please check if the system is running.")

with col1:
    if no_data:
        st.metric(label="Temperature", value="No data")
    else:
        st.metric(
            label="Temperature",
            value=f"{st.session_state.system_status['temperature']} °C",
            delta=round(random.uniform(-0.5, 0.5), 1),
        )

with col2:
    if no_data:
        st.metric(label="Pressure", value="No data")
    else:
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
    if no_data:
        st.metric(label="pH Level", value="No data")
    else:
        st.metric(
            label="pH Level",
            value=st.session_state.system_status["ph_level"],
            delta=round(random.uniform(-0.2, 0.2), 1),
        )

with col4:
    if no_data:
        st.metric(label="Dissolved Oxygen", value="No data")
    else:
        st.metric(
            label="Dissolved Oxygen",
            value=f"{st.session_state.system_status['dissolved_oxygen']} mg/L",
            delta=round(random.uniform(-0.5, 0.5), 2),
        )

# Historical data chart
st.subheader("Fermentation History (Last 48 Hours)")
historical_data = api.get_historical_data()
no_historical_data = historical_data.get('no_data_available', False)

# Create DataFrames with proper structure for charts
chart_tab1, chart_tab2, chart_tab3, chart_tab4 = st.tabs(
    ["Temperature", "Pressure", "pH", "Dissolved Oxygen"]
)

# Display message when no historical data is available
if no_historical_data:
    for tab in [chart_tab1, chart_tab2, chart_tab3, chart_tab4]:
        with tab:
            st.info("No historical data available from the fermentation prototype.")
else:
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
    st.write("Critical Operations (Require Physical Access)")

    with st.form("critical_form"):
        pressure_set = st.slider("Set Pressure (bar)", 0.5, 3.0, 1.5, 0.1)
        verification_code = st.text_input("Physical Verification Code", type="password")
        critical_submitted = st.form_submit_button("Send Command")

        if critical_submitted:
            if verification_code:
                result = api.send_command("set_pressure", pressure_set, verification_code)

                if result["success"]:
                    st.success(result["message"])
                else:
                    st.error(result["message"])
            else:
                st.error("Verification code required for critical operations")
