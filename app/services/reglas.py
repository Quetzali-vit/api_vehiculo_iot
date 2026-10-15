from app.core.exceptions import Conflicto, NoEncontrado
from app.db.database import SesionSP
from app.repositories.comando_repository import ComandoRepository
from app.repositories.demo_repository import DemoRepository
from app.repositories.vehiculo_repository import VehiculoRepository


class ReglasNegocio:
    """Validaciones compartidas: existencia, pertenencia y estado activo."""

    def __init__(self, vehiculos: VehiculoRepository, comandos: ComandoRepository, demos: DemoRepository):
        self._vehiculos = vehiculos
        self._comandos = comandos
        self._demos = demos

    def vehiculo(self, sesion: SesionSP, id_vehiculo: int) -> dict:
        vehiculo = self._vehiculos.obtener(sesion, id_vehiculo)
        if vehiculo is None:
            raise NoEncontrado(f"El vehículo {id_vehiculo} no existe")
        return vehiculo

    def vehiculo_activo(self, sesion: SesionSP, id_vehiculo: int) -> dict:
        vehiculo = self.vehiculo(sesion, id_vehiculo)
        if not vehiculo["activo"]:
            raise Conflicto(f"El vehículo {id_vehiculo} está inactivo")
        return vehiculo

    def comando_del_vehiculo(self, sesion: SesionSP, id_vehiculo: int, id_comando: int) -> dict:
        """El comando debe pertenecer al catálogo de ese vehículo; los de otro vehículo se rechazan."""
        for comando in self._comandos.listar_por_vehiculo(sesion, id_vehiculo):
            if comando["id_comando"] == id_comando:
                return comando
        raise NoEncontrado(f"El comando {id_comando} no pertenece al vehículo {id_vehiculo}")

    def comando_por_codigo(self, sesion: SesionSP, id_vehiculo: int, codigo: int) -> dict:
        for comando in self._comandos.listar_por_vehiculo(sesion, id_vehiculo):
            if comando["codigo"] == codigo:
                return comando
        raise NoEncontrado(f"El vehículo {id_vehiculo} no tiene un comando con código {codigo}")

    def comando_activo(self, comando: dict) -> dict:
        if not comando["activo"]:
            raise Conflicto(f"El comando {comando['nombre']} está inactivo")
        return comando

    def demo_del_vehiculo(self, sesion: SesionSP, id_vehiculo: int, id_demo: int) -> dict:
        for demo in self._demos.listar_por_vehiculo(sesion, id_vehiculo):
            if demo["id_demo"] == id_demo:
                return demo
        raise NoEncontrado(f"La DEMO {id_demo} no pertenece al vehículo {id_vehiculo}")

    def movimiento_de_demo(self, sesion: SesionSP, id_demo: int, id_demo_movimiento: int) -> dict:
        for movimiento in self._demos.listar_movimientos(sesion, id_demo):
            if movimiento["id_demo_movimiento"] == id_demo_movimiento:
                return movimiento
        raise NoEncontrado(f"El movimiento {id_demo_movimiento} no pertenece a la DEMO {id_demo}")
