from fastapi.testclient import TestClient
from main import app, last_update # Importamos tu app y la variable de tiempo
import time

# Creamos el cliente de prueba (simula ser el Arduino/Postman)
client = TestClient(app)

# 1. PRUEBA BÁSICA: ¿El servidor enciende?
def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "Backend IoT" in response.json()["message"]

# 2. PRUEBA DE PROTECCIÓN: Datos incorrectos
def test_datos_incorrectos():
    """
    Si enviamos un slot_id que NO es un número (ej: texto),
    el sistema debe rechazarlo para no dañar Firebase.
    """
    payload = {
        "slots": [
            {"slot_id": "esto_es_texto_error", "status": "libre"}
        ]
    }
    response = client.post("/api/parking/update", json=payload)
    
    # El código 422 significa "Entidad improcesable" (Error de validación)
    assert response.status_code == 422 

# 3. PRUEBA DE FUNCIONAMIENTO: Actualizar parking
def test_actualizar_parking():
    """
    Probamos enviar datos válidos de 2 sensores.
    """
    payload = {
        "slots": [
            {"slot_id": 101, "status": "ocupado"},
            {"slot_id": 102, "status": "libre"}
        ]
    }
    response = client.post("/api/parking/update", json=payload)
    
    # Esperamos código 200 (Éxito)
    assert response.status_code == 200
    # Verificamos que detectó 2 slots
    assert response.json()["total_slots"] == 2

# 4. PRUEBA DE MONITOREO: Timeout de sensores
def test_sensor_inactivo():
    """
    Simulamos que el sensor 99 dejó de enviar datos hace 15 segundos.
    """
    # Forzamos la última actualización al pasado (hace 15 seg)
    last_update[99] = time.time() - 15 
    
    # Consultamos el monitor
    response = client.get("/api/sensors/monitor")
    datos = response.json()
    
    # Verificamos que el mensaje contenga la alerta
    assert "⚠️ Sensor inactivo" in datos["sensors_monitor"]["99"]