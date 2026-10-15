from asyncio import to_thread

from fastapi import APIRouter, Depends, Path, Query

from app.dependencies import Contenedor, get_contenedor
from app.schemas.comunes import respuestas_error
from app.schemas.historial import HistorialRespuesta

router = APIRouter(prefix="/vehiculos/{id_vehiculo}/historial", tags=["Historial"])


@router.get("", response_model=HistorialRespuesta, summary="Últimos 10 movimientos individuales",
            description="Devuelve como máximo 10 movimientos individuales, del más reciente al más antiguo. "
                        "`total_registrados` indica cuántos hay en RDS y `devueltos` cuántos se muestran. "
                        "Si hay menos de 10, devuelve solo los disponibles. Los movimientos de DEMO nunca "
                        "aparecen porque no se guardan en el historial.\n\n"
                        "**SP:** `sp_obtener_vehiculo`, `sp_obtener_historial`",
            responses=respuestas_error(404, 503))
async def ultimos(id_vehiculo: int = Path(ge=1, description="Identificador del vehículo"),
                  limite: int = Query(10, ge=1, le=10, description="Cantidad máxima de registros (1 a 10)"),
                  c: Contenedor = Depends(get_contenedor)):
    return await to_thread(c.historial.ultimos, id_vehiculo, limite)
