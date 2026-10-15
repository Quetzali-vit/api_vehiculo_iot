from asyncio import to_thread

from fastapi import APIRouter, Depends, Path

from app.core.security import requiere_api_key
from app.dependencies import Contenedor, get_contenedor
from app.schemas.comunes import respuestas_error
from app.schemas.estado import EstadoActualizar, EstadoRespuesta

router = APIRouter(prefix="/vehiculos/{id_vehiculo}/estado", tags=["Estado"])
IdVehiculo = Path(ge=1, description="Identificador del vehículo")


@router.get("", response_model=EstadoRespuesta, summary="Último estado del vehículo",
            description="Si el vehículo existe pero aún no tiene estado, responde 200 con el comando vacío.\n\n"
                        "**SP:** `sp_obtener_vehiculo`, `sp_obtener_estado`",
            responses=respuestas_error(404, 503))
async def obtener(id_vehiculo: int = IdVehiculo, c: Contenedor = Depends(get_contenedor)):
    return await to_thread(c.estados.obtener, id_vehiculo)


@router.post("", response_model=EstadoRespuesta, summary="Actualizar el estado manualmente",
             description="Fija el comando actual y el campo `conectado` (lo usará el ESP32 en prácticas "
                         "posteriores). No escribe en el historial. Requiere `X-API-Key`.\n\n"
                         "**SP:** `sp_obtener_vehiculo`, `sp_obtener_comandos_vehiculo`, `sp_actualizar_estado`, "
                         "`sp_obtener_estado`",
             dependencies=[Depends(requiere_api_key)], responses=respuestas_error(401, 403, 404, 503))
async def actualizar(datos: EstadoActualizar, id_vehiculo: int = IdVehiculo,
                     c: Contenedor = Depends(get_contenedor)):
    return await to_thread(c.estados.actualizar, id_vehiculo, datos)
