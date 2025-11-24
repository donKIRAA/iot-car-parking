from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from models import ParkingUpdate, ParkingSlot
from firebase_utils import save_parking_data, get_all_parking_data
import time

app = FastAPI(title="Backend IoT - Gestión de Estacionamientos")

# 🌐 Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro de última actualización de cada sensor
last_update = {}

# --- ENDPOINT PARA RECIBIR VARIOS SLOTS ---
@app.post("/api/parking/update")
def update_parking(data: ParkingUpdate):
    """
    Recibe varios datos del ESP32 (array de plazas)
    y los guarda en Firebase.
    """
    for slot in data.slots:
        # Guardamos solo ID y STATUS
        save_parking_data(slot.slot_id, slot.status)
        last_update[slot.slot_id] = time.time()

    return {
        "message": "✅ Datos de plazas actualizados correctamente",
        "total_slots": len(data.slots),
        "slots": [
            {"slot_id": s.slot_id, "status": s.status}
            for s in data.slots
        ]
    }

# --- ENDPOINT PARA CONSULTAR ESTADO ---
@app.get("/api/parking/status")
def get_status():
    """
    Devuelve el estado actual de todas las plazas almacenadas en Firebase.
    """
    data = get_all_parking_data()
    if not data:
        return {"message": "⚠️ No hay datos disponibles aún."}
    return {"parking_slots": data}

# --- MONITOREAR SENSORES ---
@app.get("/api/sensors/monitor")
def monitor_sensors():
    """
    Verifica si los sensores siguen enviando datos.
    """
    current_time = time.time()
    sensors_status = {}
    timeout = 10  # segundos sin recibir datos

    for slot_id, last_time in last_update.items():
        elapsed = current_time - last_time
        if elapsed > timeout:
            sensors_status[slot_id] = "⚠️ Sensor inactivo (sin datos recientes)"
        else:
            sensors_status[slot_id] = "✅ Sensor funcionando correctamente"

    if not sensors_status:
        return {"message": "⏳ Aún no se han recibido datos de los sensores."}

    return {"sensors_monitor": sensors_status}

# --- ENDPOINT RAÍZ ---
@app.get("/")
def root(request: Request):
    base_url = str(request.base_url).rstrip("/")
    routes = {
        "Actualizar plazas": f"{base_url}/api/parking/update",
        "Ver estado actual": f"{base_url}/api/parking/status",
        "Monitorear sensores": f"{base_url}/api/sensors/monitor",
    }

    return {
        "message": "🚗 Backend IoT - Sistema de Estacionamiento Inteligente funcionando correctamente",
        "available_endpoints": routes
    }