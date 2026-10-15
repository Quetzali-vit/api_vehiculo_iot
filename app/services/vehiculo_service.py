from app.db.database import Database
from app.repositories.comando_repository import ComandoRepository
from app.repositories.demo_repository import DemoRepository
from app.repositories.estado_repository import EstadoRepository
from app.repositories.vehiculo_repository import VehiculoRepository
from app.schemas.vehiculo import VehiculoActualizar, VehiculoCrear
from app.services.reglas import ReglasNegocio


class VehiculoService:
    def __init__(self, db: Database, reglas: ReglasNegocio, vehiculos: VehiculoRepository,
                 comandos: ComandoRepository, estados: EstadoRepository, demos: DemoRepository):
        self._db = db
        self._reglas = reglas
        self._vehiculos = vehiculos
        self._comandos = comandos
        self._estados = estados
        self._demos = demos

    def listar(self) -> list[dict]:
        with self._db.transaccion() as sesion:
            return self._vehiculos.listar(sesion)

    def detalle(self, id_vehiculo: int) -> dict:
        """Vehículo con sus comandos, último estado y DEMO asociadas."""
        with self._db.transaccion() as sesion:
            vehiculo = self._reglas.vehiculo(sesion, id_vehiculo)
            return {
                **vehiculo,
                "comandos": self._comandos.listar_por_vehiculo(sesion, id_vehiculo),
                "estado": self._estados.obtener(sesion, id_vehiculo),
                "demos": self._demos.listar_por_vehiculo(sesion, id_vehiculo),
            }

    def crear(self, datos: VehiculoCrear) -> int:
        with self._db.transaccion() as sesion:
            return self._vehiculos.crear(sesion, datos.nombre, datos.modelo, datos.descripcion, datos.microcontrolador)

    def actualizar(self, id_vehiculo: int, cambios: VehiculoActualizar) -> dict:
        with self._db.transaccion() as sesion:
            actual = self._reglas.vehiculo(sesion, id_vehiculo)
            nuevo = {**actual, **cambios.model_dump(exclude_unset=True)}
            self._vehiculos.actualizar(sesion, id_vehiculo, nuevo["nombre"], nuevo["modelo"], nuevo["descripcion"],
                                       nuevo["microcontrolador"], bool(nuevo["activo"]))
            return self._vehiculos.obtener(sesion, id_vehiculo)

    def eliminar(self, id_vehiculo: int) -> None:
        with self._db.transaccion() as sesion:
            self._reglas.vehiculo(sesion, id_vehiculo)
            self._vehiculos.eliminar(sesion, id_vehiculo)
