from datetime import datetime

from pydantic import BaseModel, Field


class EstadoRespuesta(BaseModel):
    id_vehiculo: int
    vehiculo: str
    id_comando: int | None
    comando: str | None
    codigo: int | None
    conectado: bool
    fecha_actualizacion: datetime | None


class EstadoActualizar(BaseModel):
    """Cambio manual del estado (por ejemplo, cuando el ESP32 reporte su conexión)."""
    id_comando: int | None = Field(default=None, ge=1, description="Comando actual; null para dejarlo vacío")
    conectado: bool = Field(description="Si el microcontrolador está conectado")
