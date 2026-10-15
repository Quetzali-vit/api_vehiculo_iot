from datetime import datetime

from pydantic import BaseModel


class HistorialItem(BaseModel):
    id_historial: int
    id_vehiculo: int
    comando: str | None
    codigo: int | None
    fecha_hora: datetime
    origen: str


class HistorialRespuesta(BaseModel):
    id_vehiculo: int
    limite: int
    total_registrados: int
    devueltos: int
    movimientos: list[HistorialItem]
