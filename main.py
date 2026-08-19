from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import sqlite3
import uvicorn
from datetime import datetime

app = FastAPI()


def init_db():
    conn = sqlite3.connect('disaster.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sos_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lat REAL,
            lng REAL,
            emergency_type TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()


@app.get("/", response_class=HTMLResponse)
def read_root():
    return FileResponse("app.html")

@app.get("/admin", response_class=HTMLResponse)
def read_admin():
    return FileResponse("index.html")

@app.get("/manifest.json")
def get_manifest():
    return FileResponse("manifest.json")

@app.get("/sw.js")
def get_sw():
    return FileResponse("sw.js")


@app.post("/api/sos")
async def trigger_sos(lat: float, lng: float, emergency_type: str = "CITIZEN_MOBILE_GPS_SOS"):
    conn = sqlite3.connect('disaster.db')
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO sos_alerts (lat, lng, emergency_type, timestamp) VALUES (?, ?, ?, ?)",
                   (lat, lng, emergency_type, now_str))
    conn.commit()
    conn.close()
    return {"status": "success", "message": "Emergency SOS Logged in Database"}


@app.get("/api/sos_list")
def get_sos_list():
    conn = sqlite3.connect('disaster.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, lat, lng, emergency_type, timestamp FROM sos_alerts ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    
    result = []
    for r in rows:
        result.append({
            "id": r[0],
            "lat": r[1],
            "lng": r[2],
            "emergency_type": r[3],
            "timestamp": r[4]
        })
    return result

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)