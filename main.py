import os
import sqlite3
from datetime import datetime
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

app = FastAPI(title="HimResilience API", version="1.0")

# Base directory for reliable file serving on cloud
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Database Setup
def init_db():
    db_path = os.path.join(BASE_DIR, "disaster.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sos_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lat REAL,
            lng REAL,
            emergency_type TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

class SOSRequest(BaseModel):
    lat: float
    lng: float
    emergency_type: str = "CRITICAL_LIVE_CITIZEN_SOS"

@app.get("/")
def read_root():
    app_file = os.path.join(BASE_DIR, "app.html")
    return FileResponse(app_file, media_type="text/html")

@app.get("/admin")
def read_admin():
    admin_file = os.path.join(BASE_DIR, "index.html")
    return FileResponse(admin_file, media_type="text/html")

@app.get("/sw.js")
def read_sw():
    sw_file = os.path.join(BASE_DIR, "sw.js")
    return FileResponse(sw_file, media_type="application/javascript")

@app.post("/api/sos")
def create_sos(sos: SOSRequest):
    db_path = os.path.join(BASE_DIR, "disaster.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    time_now = datetime.now().strftime("%H:%M:%S")
    cursor.execute(
        "INSERT INTO sos_alerts (lat, lng, emergency_type, timestamp) VALUES (?, ?, ?, ?)",
        (sos.lat, sos.lng, sos.emergency_type, time_now)
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return {"status": "success", "id": new_id}

@app.get("/api/sos_list")
def get_sos_list():
    db_path = os.path.join(BASE_DIR, "disaster.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, lat, lng, emergency_type, timestamp FROM sos_alerts ORDER BY id DESC LIMIT 20")
    rows = cursor.fetchall()
    conn.close()
    
    alerts = []
    for r in rows:
        alerts.append({
            "id": r[0],
            "lat": r[1],
            "lng": r[2],
            "emergency_type": r[3],
            "timestamp": r[4]
        })
    return alerts