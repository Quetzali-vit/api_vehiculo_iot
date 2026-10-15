from fastapi import APIRouter, Depends, Path, status

from app.core.security import requiere_api_key
from app.dependencies import Contenedor, get_contenedor
from app.schemas.comunes import respuestas_error
from app.schemas.movimiento import MovimientoRespuesta, MovimientoSolicitud

router = APIRouter(prefix="/vehiculos/{id_vehiculo}/movimientos", tags=["Movimientos"])


@router.post("", response_model=MovimientoRespuesta, status_code=status.HTTP_201_CREATED,
             summary="Ejecutar un movimiento individual",
             description="Valida que el vehículo exista y esté activo, y que el comando exista, esté activo y "
                         "pertenezca a ese vehículo. Después guarda el estado y el historial **en una sola "
                         "transacción** y, ya confirmada, publica el evento `movimiento` por WebSocket. "
                         "Si hay una DEMO en curso responde 409, salvo con DETENER, que la cancela primero. "
                         "Requiere `X-API-Key`.\n\n"
                         "**SP:** `sp_obtener_vehiculo`, `sp_obtener_comandos_vehiculo`, `sp_obtener_estado`, "
                         "`sp_actualizar_estado`, `sp_registrar_historial`",
             dependencies=[Depends(requiere_api_key)], responses=respuestas_error(401, 403, 404, 409, 503))
async def ejecutar(solicitud: MovimientoSolicitud,
                   id_vehiculo: int = Path(ge=1, description="Identificador del vehículo"),
                   c: Contenedor = Depends(get_contenedor)):
    evento = await c.movimientos.ejecutar(id_vehiculo, solicitud)
    return {"mensaje": "Movimiento registrado y notificado", **evento}
