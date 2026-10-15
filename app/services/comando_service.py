from app.db.database import Database
from app.repositories.comando_repository import ComandoRepository
from app.schemas.comando import ComandoActualizar, ComandoCrear
from app.services.reglas import ReglasNegocio


class ComandoService:
    """Administra el catálogo de comandos (crear uno nuevo no es ejecutar un movimiento)."""

    def __init__(self, db: Database, reglas: ReglasNegocio, comandos: ComandoRepository):
        self._db = db
        self._reglas = reglas
        self._comandos = comandos

    def listar(self, id_vehiculo: int) -> list[dict]:
        with self._db.transaccion() as sesion:
            self._reglas.vehiculo(sesion, id_vehiculo)
            return self._comandos.listar_por_vehiculo(sesion, id_vehiculo)

    def crear(self, id_vehiculo: int, datos: ComandoCrear) -> int:
        with self._db.transaccion() as sesion:
            self._reglas.vehiculo(sesion, id_vehiculo)
            return self._comandos.crear(sesion, id_vehiculo, datos.nombre, datos.codigo, datos.descripcion)

    def actualizar(self, id_vehiculo: int, id_comando: int, cambios: ComandoActualizar) -> dict:
        with self._db.transaccion() as sesion:
            actual = self._reglas.comando_del_vehiculo(sesion, id_vehiculo, id_comando)
            nuevo = {**actual, **cambios.model_dump(exclude_unset=True)}
            self._comandos.actualizar(sesion, id_comando, nuevo["nombre"], nuevo["codigo"], nuevo["descripcion"],
                                      bool(nuevo["activo"]))
            return self._reglas.comando_del_vehiculo(sesion, id_vehiculo, id_comando)

    def eliminar(self, id_vehiculo: int, id_comando: int) -> None:
        with self._db.transaccion() as sesion:
            self._reglas.comando_del_vehiculo(sesion, id_vehiculo, id_comando)
            self._comandos.eliminar(sesion, id_comando)
