import streamlit as st
import sqlite3
import pandas as pd
import random
import time
from datetime import datetime
from pathlib import Path
from PIL import Image
import io

# ---------------------------------------------------------
# APP CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(
    page_title="Drone-in-a-Box Emergency Response",
    page_icon="🚁",
    layout="wide"
)

st.title("🚁 AI-Based Drone-in-a-Box Emergency Response Network")
st.caption("Software prototype | Drone movement and telemetry are simulated")

# ---------------------------------------------------------
# DATABASE
# ---------------------------------------------------------
# SQLite database is created in the same folder as this app.py.
# Do not delete this file if you want to keep locally stored mission records.
DB_PATH = Path(__file__).with_name("drone_missions.db")


def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def initialize_database():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS missions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                emergency TEXT NOT NULL,
                location TEXT NOT NULL,
                severity TEXT NOT NULL,
                created_at TEXT NOT NULL,
                status TEXT NOT NULL
            )
        """)
        conn.commit()


def add_mission(emergency, location, severity):
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO missions (emergency, location, severity, created_at, status)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                emergency,
                location,
                severity,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Dispatched"
            )
        )
        conn.commit()


def get_missions():
    with get_connection() as conn:
        return pd.read_sql_query(
            "SELECT * FROM missions ORDER BY id DESC",
            conn
        )


def update_mission_status(mission_id, status):
    with get_connection() as conn:
        conn.execute(
            "UPDATE missions SET status = ? WHERE id = ?",
            (status, int(mission_id))
        )
        conn.commit()


initialize_database()

# ---------------------------------------------------------
# SIDEBAR NAVIGATION
# ---------------------------------------------------------
page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Emergency Control",
        "Live Drone Tracking",
        "AI Image Analysis",
        "Mission History",
        "About & Limitations"
    ]
)

# ---------------------------------------------------------
# DASHBOARD
# ---------------------------------------------------------
if page == "Dashboard":
    st.header("📊 Mission Dashboard")

    missions = get_missions()
    total = len(missions)
    dispatched = int((missions["status"] == "Dispatched").sum()) if total else 0
    completed = int((missions["status"] == "Completed").sum()) if total else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Missions", total)
    c2.metric("Active / Dispatched", dispatched)
    c3.metric("Completed Missions", completed)

    st.subheader("Recent Emergency Missions")
    if total:
        st.dataframe(missions.head(10), use_container_width=True)
    else:
        st.info("No missions yet. Open Emergency Control and create a demo mission.")

    st.info(
        "Prototype flow: Emergency alert → Mission record → Simulated drone tracking "
        "→ AI image object detection → Mission history."
    )

# ---------------------------------------------------------
# EMERGENCY CONTROL
# ---------------------------------------------------------
elif page == "Emergency Control":
    st.header("🚨 Emergency Control Center")
    st.write("Create an emergency mission and save it in the SQLite database.")

    with st.form("emergency_form"):
        emergency = st.selectbox(
            "Emergency Type",
            [
                "Fire",
                "Flood",
                "Road Accident",
                "Search and Rescue",
                "Building Collapse",
                "Other"
            ]
        )
        location = st.text_input(
            "Emergency Location",
            placeholder="Example: Loni, Ahmednagar"
        )
        severity = st.select_slider(
            "Emergency Severity",
            options=["Low", "Medium", "High", "Critical"],
            value="High"
        )
        submitted = st.form_submit_button("🚁 Dispatch Drone")

    if submitted:
        if not location.strip():
            st.error("Please enter the emergency location.")
        else:
            add_mission(emergency, location.strip(), severity)
            st.success("Emergency mission created and saved in the database.")
            st.warning(
                "Demo mode: this records a mission only. It does not launch a physical drone."
            )

# ---------------------------------------------------------
# LIVE DRONE TRACKING (SIMULATION)
# ---------------------------------------------------------
elif page == "Live Drone Tracking":
    st.header("📍 Live Drone Tracking")
    st.warning(
        "Simulation only: coordinates, speed, altitude and battery below are generated "
        "for demonstration. They are not received from a real drone."
    )

    col1, col2 = st.columns(2)
    with col1:
        base_lat = st.number_input("Base latitude", value=19.9975, format="%.6f")
    with col2:
        base_lon = st.number_input("Base longitude", value=73.7898, format="%.6f")

    if st.button("▶ Start Simulated Tracking"):
        placeholder = st.empty()
        map_placeholder = st.empty()

        latitude = float(base_lat)
        longitude = float(base_lon)
        battery = 100

        for step in range(10):
            latitude += random.uniform(-0.0010, 0.0010)
            longitude += random.uniform(-0.0010, 0.0010)
            speed = random.randint(20, 55)
            altitude = random.randint(30, 100)
            battery = max(0, battery - random.randint(1, 3))

            with placeholder.container():
                a, b, c, d = st.columns(4)
                a.metric("Latitude", f"{latitude:.6f}")
                b.metric("Longitude", f"{longitude:.6f}")
                c.metric("Speed", f"{speed} km/h")
                d.metric("Battery", f"{battery}%")
                st.write(f"Altitude: **{altitude} m** | Tracking update: **{step + 1}/10**")

            map_placeholder.map(
                pd.DataFrame({"lat": [latitude], "lon": [longitude]}),
                zoom=14
            )
            time.sleep(0.7)

        st.success("Simulated tracking completed.")

# ---------------------------------------------------------
# AI IMAGE ANALYSIS - YOLOv8
# ---------------------------------------------------------
elif page == "AI Image Analysis":
    st.header("🤖 AI Image Analysis")
    st.write(
        "Upload an image. The YOLOv8 model detects objects visible in the image."
    )
    st.caption(
        "This demo uses a general-purpose pretrained YOLOv8 model, not a specialist "
        "fire, flood or disaster-detection model."
    )

    uploaded_file = st.file_uploader(
        "Upload emergency image",
        type=["jpg", "jpeg", "png"]
    )

    if uploaded_file is not None:
        try:
            image = Image.open(uploaded_file).convert("RGB")
            st.image(image, caption="Uploaded Image", use_container_width=True)

            if st.button("🔍 Analyze Image"):
                try:
                    from ultralytics import YOLO

                    @st.cache_resource
                    def load_yolo_model():
                        return YOLO("yolov8n.pt")

                    with st.spinner("Loading YOLOv8 and analyzing image..."):
                        model = load_yolo_model()
                        results = model.predict(source=image, conf=0.25, verbose=False)

                    result = results[0]
                    annotated_image = result.plot()
                    st.subheader("Detection Output")
                    st.image(
                        annotated_image,
                        caption="YOLOv8 detected objects",
                        channels="BGR",
                        use_container_width=True
                    )

                    if result.boxes is not None and len(result.boxes) > 0:
                        st.success(f"{len(result.boxes)} object(s) detected.")
                        detections = []
                        for box in result.boxes:
                            class_id = int(box.cls[0].item())
                            confidence = float(box.conf[0].item())
                            detections.append({
                                "Object": model.names[class_id],
                                "Confidence": f"{confidence * 100:.2f}%"
                            })
                        st.dataframe(
                            pd.DataFrame(detections),
                            use_container_width=True
                        )
                    else:
                        st.warning("No objects detected in this image.")

                except ImportError:
                    st.error(
                        "Ultralytics is not installed. Add 'ultralytics' to "
                        "requirements.txt and redeploy, or run: pip install ultralytics"
                    )
                except Exception as error:
                    st.error(f"Image analysis failed: {error}")
                    st.info(
                        "Check your internet connection for the first model download "
                        "and confirm ultralytics is installed."
                    )

        except Exception as error:
            st.error(f"Could not open this image: {error}")

# ---------------------------------------------------------
# MISSION HISTORY
# ---------------------------------------------------------
elif page == "Mission History":
    st.header("🗂️ Mission History")
    missions = get_missions()

    if missions.empty:
        st.info("No mission records available.")
    else:
        st.dataframe(missions, use_container_width=True)

        mission_ids = missions["id"].tolist()
        selected_id = st.selectbox("Select mission ID to update", mission_ids)
        new_status = st.selectbox(
            "New mission status",
            ["Dispatched", "In Progress", "Completed", "Cancelled"]
        )

        if st.button("Update Mission Status"):
            update_mission_status(selected_id, new_status)
            st.success(f"Mission #{selected_id} updated to {new_status}.")
            st.rerun()

        csv_data = missions.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇ Download Mission History (CSV)",
            data=csv_data,
            file_name="drone_mission_history.csv",
            mime="text/csv"
        )

# ---------------------------------------------------------
# ABOUT AND LIMITATIONS
# ---------------------------------------------------------
elif page == "About & Limitations":
    st.header("ℹ️ About the Project")

    st.markdown("""
    **AI-Based Drone-in-a-Box Emergency Response Network** is a software prototype
    designed to demonstrate how drones could support emergency response.

    ### Main modules
    1. Emergency Control – create and save emergency mission records.
    2. Live Drone Tracking – demonstrate simulated location and telemetry.
    3. AI Image Analysis – use YOLOv8 to detect general objects in an uploaded image.
    4. Mission History – view, update and export saved mission records.
    5. SQLite Database – store mission details locally.

    ### Proposed hardware (not connected in this software demo)
    - Drone with Pixhawk flight controller
    - Raspberry Pi or NVIDIA Jetson edge computer
    - GPS and camera (RGB / thermal)
    - ESP32-based docking station and charging system
    - 4G / 5G communication

    ### Important limitations
    - No physical drone is controlled by this application.
    - Tracking values are simulated, not live GPS or battery telemetry.
    - YOLOv8n is a general object-detection model; it does not reliably confirm fire,
      flood, injury or other emergencies.
    - SQLite stores data in a local file. On hosted platforms, local files may not
      provide permanent storage across restarts or redeployments.
    """)

st.sidebar.markdown("---")
st.sidebar.caption("Prototype version | SQLite + YOLOv8")
