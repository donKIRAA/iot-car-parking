from pydantic import BaseModel
from typing import List

class ParkingSlot(BaseModel):
    slot_id: int
    status: str

class ParkingUpdate(BaseModel):
    slots: List[ParkingSlot]

class UserCreate(BaseModel):
    email: str
    password: str