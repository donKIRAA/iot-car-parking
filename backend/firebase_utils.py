import firebase_admin
from firebase_admin import credentials, db
import os

# Asegúrate de que el nombre del archivo coincida con el que tienes en tu carpeta
KEY_PATH = "serviceAccountKey.json"
DATABASE_URL = "https://iot-car-parking-43374-default-rtdb.firebaseio.com/"

# Inicializar Firebase (solo una vez)
if not firebase_admin._apps:
    cred = credentials.Certificate(KEY_PATH)
    firebase_admin.initialize_app(cred, {
        "databaseURL": DATABASE_URL
    })

def save_parking_data(slot_id, status):
    """
    Guarda/actualiza /parking_slots/{slot_id}
    """
    slot_key = str(slot_id)
    ref = db.reference(f"/parking_slots/{slot_key}")
    # Se guarda solo el status
    ref.set({
        "status": status
    })

def get_all_parking_data():
    """
    Lee /parking_slots y retorna una LISTA de objetos.
    """
    ref = db.reference("/parking_slots")
    data = ref.get()

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
                "status": slot_data.get("status")
            })
        return slots

    if isinstance(data, list):
        for idx, slot_data in enumerate(data):
            if slot_data is None:
                continue
            slot_id = str(idx)
            slots.append({
                "slot_id": slot_id,
                "status": slot_data.get("status")
            })
        return slots

    return data