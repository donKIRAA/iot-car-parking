import firebase_admin
from firebase_admin import credentials, db
import os

# RUTA a tu JSON -> si ya lo pusiste en la carpeta backend, basta con el nombre
KEY_PATH = "serviceAccountKey.json"
DATABASE_URL = "https://iot-car-parking-43374-default-rtdb.firebaseio.com/"

# Inicializar Firebase (solo una vez)
if not firebase_admin._apps:
    cred = credentials.Certificate(KEY_PATH)
    firebase_admin.initialize_app(cred, {
        "databaseURL": DATABASE_URL
    })

def save_parking_data(slot_id, status, distance):
    """
    Guarda/actualiza /parking_slots/{slot_id}
    Aseguramos que slot_id se guarde como cadena (evita conversión a array).
    """
    slot_key = str(slot_id)
    ref = db.reference(f"/parking_slots/{slot_key}")
    ref.set({
        "status": status,
        "distance": float(distance)
    })

def get_all_parking_data():
    """
    Lee /parking_slots y retorna una LISTA de objetos:
    [ { "slot_id": "1", "status": "...", "distance": ... }, ... ]
    Esta función maneja tanto dicts (Firebase devuelve objeto) como listas
    (cuando las keys son numéricas Firebase puede devolver un array).
    """
    ref = db.reference("/parking_slots")
    data = ref.get()
    # log para depuración
    print("📡 Datos obtenidos de Firebase (raw):", data)

    if not data:
        return None

    slots = []

    if isinstance(data, dict):
        # formato esperado: {"1": {...}, "2": {...}}
        for slot_id, slot_data in data.items():
            if slot_data is None:
                continue
            slots.append({
                "slot_id": str(slot_id),
                "status": slot_data.get("status"),
                "distance": slot_data.get("distance")
            })
        return slots

    if isinstance(data, list):
        # formato: [None, {...}, {...}] -> índice = slot_id
        for idx, slot_data in enumerate(data):
            if slot_data is None:
                continue
            # si tus keys reales empiezan en 1, idx corresponde a ese número
            slot_id = str(idx)
            slots.append({
                "slot_id": slot_id,
                "status": slot_data.get("status"),
                "distance": slot_data.get("distance")
            })
        return slots

    # fallback: devuelve datos tal cual en caso raro
    return data
