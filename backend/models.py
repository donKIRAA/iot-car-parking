from pydantic import BaseModel

class ParkingData(BaseModel):
    slot_id: int        # ID de la plaza (por ejemplo, "P1", "P2")
    status: str          # Estado: "ocupado" o "libre"
    distance: float      # Distancia medida por el sensor (cm)
