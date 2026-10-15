from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.comando import ComandoRespuesta
from app.schemas.demo import DemoRespuesta
from app.schemas.estado import EstadoRespuesta


class VehiculoCrear(BaseModel):
    nombre: str = Field(min_length=1, max_length=80, examples=["Retroexcavadora IoT"])
    modelo: str | None = Field(default=None, max_length=80, examples=["Retroexcavadora RC a escala"])
    descripcion: str | None = Field(default=None, max_length=255)
    microcontrolador: str | None = Field(default=None, max_length=50, examples=["ESP32"])


class VehiculoActualizar(BaseModel):
    """Solo se cambian los campos enviados; los demás conservan su valor actual."""
    nombre: str | None = Field(default=None, min_length=1, max_length=80)
    modelo: str | None = Field(default=None, max_length=80)
    descripcion: str | None = Field(default=None, max_length=255)
    microcontrolador: str | None = Field(default=None, max_length=50)
    activo: bool | None = None


class VehiculoRespuesta(BaseModel):
    id_vehiculo: int
    nombre: str
    modelo: str | None
    descripcion: str | None
    microcontrolador: str | None
    fecha_registro: datetime | None
    activo: bool


class VehiculoDetalle(VehiculoRespuesta):
    comandos: list[ComandoRespuesta]
    estado: EstadoRespuesta | None
    demos: list[DemoRespuesta]


class VehiculoCreado(BaseModel):
    mensaje: str
    id_vehiculo: int
