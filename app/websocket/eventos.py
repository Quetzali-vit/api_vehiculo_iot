from datetime import datetime, timezone
from typing import Any


class TipoEvento:
    ESTADO_ACTUAL = "estado_actual"
    MOVIMIENTO = "movimiento"
    DEMO_INICIO = "demo_inicio"
    DEMO_MOVIMIENTO = "demo_movimiento"
    DEMO_FIN = "demo_fin"
    DEMO_CANCELADA = "demo_cancelada"
    DEMO_ERROR = "demo_error"
    PONG = "pong"
    ERROR = "error"


def crear_evento(evento: str, id_vehiculo: int, comando: str | None = None, codigo: int | None = None,
                 **datos: Any) -> dict:
    """Mensaje JSON común: tipo de evento, vehículo, comando, código y marca temporal."""
    return {
        "evento": evento,
        "id_vehiculo": id_vehiculo,
        "comando": comando,
        "codigo": codigo,
        **datos,
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
    }
