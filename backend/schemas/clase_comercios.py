from pydantic import BaseModel


class ComercioBase(BaseModel):
    nombre: str
    email: str


class ComercioCreate(ComercioBase):
    pass


class Comercio(ComercioBase):
    id: int
    api_key: str