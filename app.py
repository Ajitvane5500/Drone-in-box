import streamlit as st
import pandas as pd
import random
import time
from datetime import datetime

st.set_page_config(
    page_title="Drone Emergency Network",
    page_icon="🚁",
    layout="wide"
)

st.title("🚁 AI-Based Drone-in-a-Box Emergency Response Network")

st.success("Emergency Response System Online")

# Sidebar
st.sidebar.title("Control Center")

page = st.sidebar.radio(
    "Select Module",
    [
        "Dashboard",
        "Emergency Control",
        "Live Drone Tracking",
        "Mission History"
    ]
)

# Session State
if "mission" not in st.session_state:
    st.session_state.mission = "Standby"

if "battery" not in st.session_state:
    st.session_state.battery = 100

if "latitude" not in st.session_state:
    st.session_state.latitude = 18.5204

if "longitude" not in st.session_state:
    st.session_state.longitude = 73.8567

if "history" not in st.session_state:
    st.session_state.history = []

if page == "Dashboard":

    st.header("System Dashboard")

    c1, c2, c3 = st.columns(3)

    c1.metric("Drone Status", st.session_state.mission)
    c2.metric("Battery", f"{st.session_state.battery}%")
    c3.metric("Active Missions", len([
        x for x in st.session_state.history
    ]))

    st.info("Drone Emergency Response Network is Ready.")

    st.subheader("Available Features")

    st.write("✅ Emergency Detection")
    st.write("✅ Automated Drone Dispatch Simulation")
    st.write("✅ Live Location Monitoring Simulation")
    st.write("✅ Battery and Telemetry Monitoring")
    st.write("✅ Mission History")

elif page == "Emergency Control":

    st.header("🚨 Emergency Control Center")

    emergency = st.selectbox(
        "Select Emergency Type",
        ["Fire", "Flood", "Accident", "Building Collapse"]
    )

    location = st.text_input(
        "Enter Emergency Location",
        "Pune"
    )

    severity = st.selectbox(
        "Emergency Severity",
        ["Low", "Medium", "High", "Critical"]
    )

    if st.button("🚁 DISPATCH DRONE"):

        st.session_state.mission = "Dispatched"

        st.session_state.history.append({
            "Emergency": emergency,
            "Location": location,
            "Severity": severity,
            "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Status": "Dispatched"
        })

        st.success("Drone Dispatched Successfully!")
        st.balloons()

elif page == "Live Drone Tracking":

    st.header("🛰️ Live Drone Tracking")

    st.write("Drone GPS Location: Pune (Demo Coordinates)")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Battery",
        f"{st.session_state.battery}%"
    )

    c2.metric(
        "Speed",
        f"{random.randint(25, 45)} km/h"
    )

    c3.metric(
        "Altitude",
        f"{random.randint(40, 100)} m"
    )

    st.subheader("Drone GPS Map")

    if st.session_state.mission == "Dispatched":

        st.session_state.latitude += random.uniform(-0.001, 0.001)
        st.session_state.longitude += random.uniform(-0.001, 0.001)

        st.session_state.battery = max(
            0,
            st.session_state.battery - 1
        )

    map_data = pd.DataFrame({
        "latitude": [st.session_state.latitude],
        "longitude": [st.session_state.longitude]
    })

    st.map(map_data)

    st.write(
        f"Latitude: {st.session_state.latitude:.6f}"
    )

    st.write(
        f"Longitude: {st.session_state.longitude:.6f}"
    )

    if st.session_state.mission == "Dispatched":

        if st.button("🔄 Refresh Drone Location"):
            st.rerun()

        if st.button("🏁 Complete Mission"):

            st.session_state.mission = "Completed"

            if st.session_state.history:
                st.session_state.history[-1]["Status"] = "Completed"

            st.success("Mission Completed Successfully!")

    elif st.session_state.mission == "Completed":

        st.success("Drone Mission Completed.")

    else:

        st.warning("No Active Drone Mission.")

elif page == "Mission History":

    st.header("📋 Mission History")

    if st.session_state.history:

        df = pd.DataFrame(st.session_state.history)

        st.dataframe(
            df,
            use_container_width=True
        )

    else:

        st.info("No Mission Records Available.")

st.divider()

st.caption(
    "AI-Based Drone-in-a-Box Emergency Response Network | Software Prototype"
)
