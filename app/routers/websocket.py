import asyncio
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.exceptions import ApiError, NoEncontrado
from app.dependencies import get_contenedor
from app.websocket.eventos import TipoEvento, crear_evento

logger = logging.getLogger(__name__)
router = APIRouter()


def _evento_estado(estado: dict) -> dict:
    return crear_evento(TipoEvento.ESTADO_ACTUAL, estado["id_vehiculo"], estado["comando"], estado["codigo"],
                        conectado=bool(estado["conectado"]), fecha_actualizacion=estado["fecha_actualizacion"])


@router.websocket("/ws/vehiculos/{id_vehiculo}")
async def monitorear(websocket: WebSocket, id_vehiculo: int):
    """Monitoreo de un vehículo. Documentado en README.md (Swagger no describe WebSocket)."""
    c = get_contenedor()
    await websocket.accept()

    try:
        estado = await asyncio.to_thread(c.estados.obtener, id_vehiculo)
    except ApiError as error:
        await c.gestor_ws.enviar(websocket, crear_evento(TipoEvento.ERROR, id_vehiculo, mensaje=error.mensaje))
        await websocket.close(code=4404 if isinstance(error, NoEncontrado) else 1011)
        return

    await c.gestor_ws.conectar(id_vehiculo, websocket)
    try:
        await c.gestor_ws.enviar(websocket, _evento_estado(estado))
        while True:
            texto = (await websocket.receive_text()).strip().lower()
            if texto == "ping":
                await c.gestor_ws.enviar(websocket, crear_evento(TipoEvento.PONG, id_vehiculo))
            elif texto == "estado":
                estado = await asyncio.to_thread(c.estados.obtener, id_vehiculo)
                await c.gestor_ws.enviar(websocket, _evento_estado(estado))
            else:
                await c.gestor_ws.enviar(websocket, crear_evento(
                    TipoEvento.ERROR, id_vehiculo, mensaje="Mensaje no reconocido. Usa 'ping' o 'estado'."))
    except WebSocketDisconnect:
        pass
    except Exception:
        logger.exception("Error en el WebSocket del vehículo %s", id_vehiculo)
    finally:
        await c.gestor_ws.desconectar(id_vehiculo, websocket)
