import math
import sqlite3
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st
from PIL import Image

APP_DIR = Path(__file__).parent
DB_PATH = APP_DIR / "dronebox.db"

st.set_page_config(
    page_title="Drone-in-a-Box | Emergency Response",
    page_icon="🚁",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------- DATABASE --------------------
def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS missions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                incident_type TEXT NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                station_name TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        conn.commit()

def save_mission(incident_type, lat, lon, station_name):
    with get_conn() as conn:
        cur = conn.execute(
            """INSERT INTO missions
            (incident_type, latitude, longitude, station_name, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?)""",
            (incident_type, lat, lon, station_name, "Alert Received",
             datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        conn.commit()
        return cur.lastrowid

def update_mission(mission_id, status):
    with get_conn() as conn:
        conn.execute("UPDATE missions SET status=? WHERE id=?", (status, mission_id))
        conn.commit()

def get_missions():
    with get_conn() as conn:
        return pd.read_sql_query(
            "SELECT id, incident_type, latitude, longitude, station_name, status, created_at "
            "FROM missions ORDER BY id DESC", conn
        )

init_db()

# -------------------- DEMO DATA --------------------
# These are illustrative demo stations around Pune, not real emergency facilities.
STATIONS = pd.DataFrame([
    {"Station": "Demo Drone Station A", "Latitude": 18.5204, "Longitude": 73.8567, "Status": "Available"},
    {"Station": "Demo Drone Station B", "Latitude": 18.5679, "Longitude": 73.9143, "Status": "Available"},
    {"Station": "Demo Drone Station C", "Latitude": 18.4875, "Longitude": 73.8077, "Status": "Available"},
    {"Station": "Demo Drone Station D", "Latitude": 18.6298, "Longitude": 73.7997, "Status": "Maintenance"},
])

def haversine_km(lat1, lon1, lat2, lon2):
    radius = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlon / 2) ** 2
    return 2 * radius * math.asin(math.sqrt(a))

def nearest_station(lat, lon):
    candidates = STATIONS[STATIONS["Status"] == "Available"].copy()
    candidates["Distance (km)"] = candidates.apply(
        lambda row: haversine_km(lat, lon, row["Latitude"], row["Longitude"]), axis=1
    )
    return candidates.sort_values("Distance (km)").iloc[0]

# -------------------- SIDEBAR --------------------
st.sidebar.title("🚁 DroneBox AI")
st.sidebar.caption("Emergency Response Prototype")
page = st.sidebar.radio(
    "Navigation",
    ["Overview", "Emergency Control", "AI Image Analysis", "Mission History", "About & Limitations"]
)
st.sidebar.divider()
st.sidebar.info("Prototype mode: station locations and drone movement are simulated.")

# -------------------- HEADER --------------------
st.title("🚁 AI-Based Drone-in-a-Box Emergency Response Network")
st.caption("PCCOE IGC 2026 • Theme: AI for Climate Change • Software proof-of-concept")

if page == "Overview":
    missions = get_missions()
    total = len(missions)
    active = int(missions["status"].isin(["Alert Received", "Dispatched", "At Incident"]).sum()) if total else 0
    available = int((STATIONS["Status"] == "Available").sum())

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Demo Missions", total)
    c2.metric("Active Missions", active)
    c3.metric("Available Demo Stations", available)
    c4.metric("AI Module", "Ready to test")

    st.subheader("System workflow")
    st.markdown("""
    **Emergency Alert** → **Nearest Available Demo Station** → **Dispatch Simulation**
    → **Aerial Image Analysis** → **Responder Information** → **Return to Station**
    """)
    st.subheader("Demo station locations")
    st.caption("Illustrative Pune-area coordinates used only to demonstrate distance calculation. These are not actual drone bases.")
    st.map(STATIONS.rename(columns={"Latitude": "lat", "Longitude": "lon"})[["lat", "lon"]], zoom=10)
    st.dataframe(STATIONS, use_container_width=True, hide_index=True)

    st.subheader("Recent missions")
    if missions.empty:
        st.info("No missions yet. Open Emergency Control and create a demo emergency.")
    else:
        st.dataframe(missions.head(5), use_container_width=True, hide_index=True)

elif page == "Emergency Control":
    st.header("🚨 Emergency Control Centre")
    st.write("Create a sample incident. The application calculates the nearest available demo station.")
    with st.form("emergency_form"):
        incident_type = st.selectbox(
            "Emergency type",
            ["Flood", "Forest Fire", "Road Accident", "Building Collapse", "Storm Damage", "Other"]
        )
        col1, col2 = st.columns(2)
        with col1:
            lat = st.number_input("Incident latitude", value=18.5204, format="%.6f")
        with col2:
            lon = st.number_input("Incident longitude", value=73.8567, format="%.6f")
        submitted = st.form_submit_button("🚨 Create Emergency Alert", type="primary", use_container_width=True)

    if submitted:
        nearest = nearest_station(lat, lon)
        mission_id = save_mission(incident_type, lat, lon, nearest["Station"])
        st.session_state["current_mission_id"] = mission_id
        st.session_state["current_station"] = nearest["Station"]
        st.session_state["current_distance"] = float(nearest["Distance (km)"])
        st.success(f"Demo alert #{mission_id} created. Nearest available station: {nearest['Station']}")
        st.rerun()

    mission_id = st.session_state.get("current_mission_id")
    if mission_id:
        missions = get_missions()
        current = missions[missions["id"] == mission_id]
        if not current.empty:
            mission = current.iloc[0]
            st.divider()
            st.subheader(f"Mission #{mission_id}")
            a, b, c = st.columns(3)
            a.metric("Incident", mission["incident_type"])
            b.metric("Selected station", mission["station_name"])
            c.metric("Current status", mission["status"])
            if "current_distance" in st.session_state:
                st.metric("Approx. straight-line distance", f"{st.session_state['current_distance']:.2f} km")
            st.caption("Distance is calculated using the Haversine formula. It is not a road-route distance.")

            status = mission["status"]
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                if st.button("1. Dispatch Drone", disabled=status != "Alert Received", use_container_width=True):
                    update_mission(mission_id, "Dispatched")
                    st.rerun()
            with col_b:
                if st.button("2. Mark At Incident", disabled=status != "Dispatched", use_container_width=True):
                    update_mission(mission_id, "At Incident")
                    st.rerun()
            with col_c:
                if st.button("3. Return to Station", disabled=status != "At Incident", use_container_width=True):
                    update_mission(mission_id, "Returned")
                    st.rerun()
            st.info("The buttons update a simulated mission state. No physical drone is launched or controlled.")
    else:
        st.info("Create an emergency alert to begin the demo workflow.")

elif page == "AI Image Analysis":
    st.header("🧠 AI Image Analysis")
    st.write("Upload an image to run a pretrained YOLO object-detection model.")
    st.warning(
        "The default YOLOv8 COCO model can detect common objects such as people, cars, buses and trucks. "
        "It is not a validated flood, fire, smoke, victim-rescue or disaster-detection model."
    )
    uploaded = st.file_uploader("Upload JPG, JPEG or PNG image", type=["jpg", "jpeg", "png"])
    if uploaded:
        image = Image.open(uploaded).convert("RGB")
        st.image(image, caption="Uploaded image", use_container_width=True)
        if st.button("🔍 Run AI Object Detection", type="primary"):
            with st.spinner("Loading model and analysing image. First run may download model weights..."):
                try:
                    from ultralytics import YOLO
                    model = YOLO("yolov8n.pt")
                    results = model.predict(image, conf=0.25, verbose=False)
                    result = results[0]
                    annotated = result.plot()
                    # Ultralytics returns BGR array; convert for Streamlit display.
                    import cv2
                    annotated_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
                    st.image(annotated_rgb, caption="AI detection result", use_container_width=True)
                    names = result.names
                    detections = []
                    if result.boxes is not None:
                        for box in result.boxes:
                            cls_id = int(box.cls[0].item())
                            confidence = float(box.conf[0].item())
                            detections.append({
                                "Detected object": names.get(cls_id, str(cls_id)),
                                "Confidence": f"{confidence * 100:.1f}%"
                            })
                    if detections:
                        st.success(f"Detection completed: {len(detections)} object(s) found.")
                        st.dataframe(pd.DataFrame(detections), use_container_width=True, hide_index=True)
                    else:
                        st.info("The model did not detect an object above the selected confidence threshold.")
                    st.caption("This is a general-purpose pretrained model result, not a safety-critical emergency decision.")
                except ImportError:
                    st.error("AI packages are not installed. In the terminal run: pip install -r requirements.txt")
                except Exception as exc:
                    st.error(f"Could not run the model: {exc}")
                    st.caption("Check your internet connection for the first model download, then try again.")

elif page == "Mission History":
    st.header("📋 Mission History")
    missions = get_missions()
    if missions.empty:
        st.info("No demo missions recorded yet.")
    else:
        st.dataframe(missions, use_container_width=True, hide_index=True)
        csv = missions.to_csv(index=False).encode("utf-8")
        st.download_button("Download mission history CSV", csv, "mission_history.csv", "text/csv")

else:
    st.header("ℹ️ About the Prototype")
    st.markdown("""
    ### Objective
    Demonstrate how an AI-enabled drone response workflow could provide early aerial information during
    climate-related emergencies and other incidents.

    ### Implemented in this software prototype
    - Emergency alert form
    - Nearest available demo-station selection using Haversine distance
    - Mission status workflow: Alert Received → Dispatched → At Incident → Returned
    - SQLite mission-history storage
    - Optional YOLOv8 image object detection

    ### Planned future integration (not physically demonstrated)
    - Real drone and flight controller integration
    - GPS telemetry and live video stream
    - Thermal, smoke and gas sensors
    - Real docking station and automatic charging
    - Validated custom AI models for fire, smoke, flood damage and victim detection
    - Field testing, safety approvals and emergency-service integration

    ### Climate-change relevance
    The concept can support faster assessment of floods, forest fires, storms and extreme-weather damage.
    The prototype demonstrates the software workflow; actual climate impact must be measured in controlled
    field trials against a defined baseline.
    """)
    st.error("This is an educational proof-of-concept. It must not be used for real emergency dispatch or rescue decisions.")

st.sidebar.divider()
st.sidebar.caption("Built as a student prototype • Demo data only")
