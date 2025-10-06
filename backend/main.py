from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware  # 👈 IMPORTANTE
from models import ParkingData
from firebase_utils import save_parking_data, get_all_parking_data
import time

app = FastAPI(title="Backend IoT - Gestión de Estacionamientos")

# 🌐 Configurar CORS - MUY IMPORTANTE
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todos los orígenes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro de última actualización de cada sensor
last_update = {}

@app.post("/api/parking/update")
def update_parking(data: ParkingData):
    """
    Recibe los datos del ESP32 (slot_id, status, distance)
    y los guarda en Firebase. También registra el tiempo del último envío.
    """
    save_parking_data(data.slot_id, data.status, data.distance)
    last_update[data.slot_id] = time.time()
    return {
        "message": f"✅ Plaza {data.slot_id} actualizada a {data.status}",
        "slot_id": data.slot_id,
        "status": data.status,
        "distance": data.distance
    }

@app.get("/api/parking/status")
def get_status():
    """
    Devuelve el estado actual de todas las plazas almacenadas en Firebase.
    """
    data = get_all_parking_data()
    if not data:
        return {"message": "⚠️ No hay datos disponibles aún."}
    return {"parking_slots": data}

@app.get("/api/sensors/monitor")
def monitor_sensors():
    """
    Verifica la funcionalidad de los sensores. Si uno no envía datos en más de 10s,
    se marca como inactivo.
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

@app.get("/")
def root(request: Request):
    """
    Endpoint raíz — genera las rutas completas automáticamente.
    """
    base_url = str(request.base_url).rstrip("/")
    routes = {
        "Actualizar plaza": f"{base_url}/api/parking/update",
        "Ver estado actual": f"{base_url}/api/parking/status",
        "Monitorear sensores": f"{base_url}/api/sensors/monitor",
    }

    return {
        "message": "🚗 Backend IoT - Sistema de Estacionamiento Inteligente funcionando correctamente",
        "available_endpoints": routes
    }