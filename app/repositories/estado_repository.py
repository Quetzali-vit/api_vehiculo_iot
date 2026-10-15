from app.db.database import SesionSP


class EstadoRepository:
    """Acceso a los SP de la tabla estado_vehiculo."""

    def actualizar(self, sesion: SesionSP, id_vehiculo: int, id_comando: int | None, conectado: bool) -> None:
        sesion.llamar("sp_actualizar_estado", id_vehiculo, id_comando, conectado)

    def obtener(self, sesion: SesionSP, id_vehiculo: int) -> dict | None:
        filas = sesion.llamar("sp_obtener_estado", id_vehiculo)
        return filas[0] if filas else None
