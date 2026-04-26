from pydantic import BaseModel, Field
from datetime import date
from typing import Optional


class PagoBase(BaseModel):
    monto: float = Field(..., gt=0)
    fecha: date
    estado: str


class PagoCreate(PagoBase):
    pass


class PagoUpdate(PagoBase):
    pass


class Pago(PagoBase):
    id: int
    comercio_id: Optional[int] = None
    mp_preference_id: Optional[str] = None
    mp_init_point: Optional[str] = None
    mp_payment_id: Optional[str] = None