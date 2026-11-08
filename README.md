# AI-Based Drone-in-a-Box Emergency Response Network

A student-friendly Streamlit proof-of-concept for PCCOE IGC 2026 Round 2.

## Features
- Emergency alert form
- Nearest available demo station selection using Haversine distance
- Simulated mission workflow: Alert Received -> Dispatched -> At Incident -> Returned
- SQLite mission history
- Optional YOLOv8 image object detection for common COCO objects

## Important honesty / safety note
This is a **software simulation**, not a real drone control system. Demo station coordinates are illustrative Pune-area points, not real emergency facilities. The pretrained YOLOv8 COCO model is a general object detector; it is **not** a validated fire, smoke, flood, victim-rescue or disaster detector. Do not use this prototype for real emergency decisions.

## 1. Install Python
Install Python 3.10 or 3.11. During Windows installation, tick **Add Python to PATH**.

## 2. Open the project in VS Code
1. Extract `DroneBox_Round2_Prototype.zip`.
2. Open VS Code.
3. Select **File -> Open Folder**.
4. Select the extracted `DroneBox_Round2_Prototype` folder.
5. Open **Terminal -> New Terminal**.

## 3. Create a virtual environment (recommended)
Windows:
```bash
py -m venv venv
venv\Scripts\activate
```

macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

## 4. Install packages
```bash
pip install -r requirements.txt
```
The Ultralytics/PyTorch dependencies are large and may take several minutes. An internet connection may be needed to install packages and download `yolov8n.pt` on the first AI run.

## 5. Run the app
```bash
streamlit run app.py
```
A browser tab should open. If not, copy the local URL shown in the terminal (usually `http://localhost:8501`).

## 6. Demo sequence for the video
1. Open **Overview** and show station cards/map.
2. Open **Emergency Control**.
3. Select Flood or Forest Fire and keep the sample coordinates, or enter another valid latitude/longitude.
4. Click **Create Emergency Alert**.
5. Click **Dispatch Drone**, then **Mark At Incident**, then **Return to Station**. Explain that these are simulated state changes.
6. Open **AI Image Analysis**, upload a clear photo containing common objects such as people or vehicles, then click **Run AI Object Detection**.
7. Open **Mission History** and show the saved mission.
8. Finish with **About & Limitations** and explain the future hardware integration.

## Troubleshooting
- `streamlit is not recognized`: activate the virtual environment and run `python -m pip install -r requirements.txt`, then `python -m streamlit run app.py`.
- Package installation error: confirm internet access and Python 3.10/3.11; retry `python -m pip install --upgrade pip`.
- AI model download fails: the dashboard and simulated emergency workflow can still be demonstrated. Retry AI detection when internet access is available.
- Port busy: run `python -m streamlit run app.py --server.port 8502`.

## Project structure
```text
DroneBox_Round2_Prototype/
├── app.py
├── requirements.txt
├── README.md
└── assets/
```
