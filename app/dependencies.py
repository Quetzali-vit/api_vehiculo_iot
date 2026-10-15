from functools import cached_property, lru_cache

from app.core.config import get_settings
from app.db.database import Database
from app.repositories.comando_repository import ComandoRepository
from app.repositories.demo_repository import DemoRepository
from app.repositories.estado_repository import EstadoRepository
from app.repositories.historial_repository import HistorialRepository
from app.repositories.vehiculo_repository import VehiculoRepository
from app.services.comando_service import ComandoService
from app.services.demo_executor import EjecutorDemos
from app.services.demo_service import DemoService
from app.services.estado_service import EstadoService
from app.services.historial_service import HistorialService
from app.services.movimiento_service import MovimientoService
from app.services.reglas import ReglasNegocio
from app.services.vehiculo_service import VehiculoService
from app.websocket.manager import GestorWebSocket


class Contenedor:
    """Crea una sola instancia de cada componente y las conecta entre sí."""

    def __init__(self):
        self.settings = get_settings()
        self.db = Database(self.settings)
        self.gestor_ws = GestorWebSocket()

        self._vehiculos = VehiculoRepository()
        self._comandos = ComandoRepository()
        self._estados = EstadoRepository()
        self._historial = HistorialRepository()
        self._demos = DemoRepository()
        self._reglas = ReglasNegocio(self._vehiculos, self._comandos, self._demos)

    @cached_property
    def vehiculos(self) -> VehiculoService:
        return VehiculoService(self.db, self._reglas, self._vehiculos, self._comandos, self._estados, self._demos)

    @cached_property
    def comandos(self) -> ComandoService:
        return ComandoService(self.db, self._reglas, self._comandos)

    @cached_property
    def estados(self) -> EstadoService:
        return EstadoService(self.db, self._reglas, self._estados)

    @cached_property
    def historial(self) -> HistorialService:
        return HistorialService(self.db, self._reglas, self._historial)

    @cached_property
    def demos(self) -> DemoService:
        return DemoService(self.db, self._reglas, self._demos, self._comandos, self._estados)

    @cached_property
    def ejecutor(self) -> EjecutorDemos:
        return EjecutorDemos(self.demos, self.gestor_ws)

    @cached_property
    def movimientos(self) -> MovimientoService:
        return MovimientoService(self.db, self._reglas, self._estados, self._historial, self.gestor_ws,
                                 self.ejecutor, self.settings.origen_movimiento)


@lru_cache
def get_contenedor() -> Contenedor:
    return Contenedor()
