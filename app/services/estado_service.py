from app.db.database import Database
from app.repositories.estado_repository import EstadoRepository
from app.schemas.estado import EstadoActualizar
from app.services.reglas import ReglasNegocio


class EstadoService:
    def __init__(self, db: Database, reglas: ReglasNegocio, estados: EstadoRepository):
        self._db = db
        self._reglas = reglas
        self._estados = estados

    def obtener(self, id_vehiculo: int) -> dict:
        """Último estado; si el vehículo aún no tiene uno, se devuelve vacío y desconectado."""
        with self._db.transaccion() as sesion:
            vehiculo = self._reglas.vehiculo(sesion, id_vehiculo)
            estado = self._estados.obtener(sesion, id_vehiculo)
        return estado or {
            "id_vehiculo": id_vehiculo,
            "vehiculo": vehiculo["nombre"],
            "id_comando": None,
            "comando": None,
            "codigo": None,
            "conectado": False,
            "fecha_actualizacion": None,
        }

    def actualizar(self, id_vehiculo: int, datos: EstadoActualizar) -> dict:
        with self._db.transaccion() as sesion:
            self._reglas.vehiculo(sesion, id_vehiculo)
            if datos.id_comando is not None:
                self._reglas.comando_del_vehiculo(sesion, id_vehiculo, datos.id_comando)
            self._estados.actualizar(sesion, id_vehiculo, datos.id_comando, datos.conectado)
            return self._estados.obtener(sesion, id_vehiculo)
