from datetime import datetime

from pydantic import BaseModel, Field, model_validator


class MovimientoSolicitud(BaseModel):
    """Movimiento individual. Envía id_comando o codigo (solo uno)."""
    id_comando: int | None = Field(default=None, ge=1, examples=[1])
    codigo: int | None = Field(default=None, ge=0, le=9999, examples=[None])
    origen: str | None = Field(default=None, min_length=1, max_length=30, pattern=r"^[A-Za-z0-9_\-]+$",
                               description="Origen que se guarda en el historial. Por defecto API-LOCAL.")

    @model_validator(mode="after")
    def _un_solo_identificador(self):
        if (self.id_comando is None) == (self.codigo is None):
            raise ValueError("Envía id_comando o codigo, pero no ambos")
        return self


class MovimientoRespuesta(BaseModel):
    mensaje: str
    evento: str
    id_vehiculo: int
    id_comando: int
    comando: str
    codigo: int
    origen: str
    conectado: bool
    timestamp: datetime
