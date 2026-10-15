from app.core.exceptions import Conflicto
from app.db.database import Database
from app.repositories.comando_repository import ComandoRepository
from app.repositories.demo_repository import DemoRepository
from app.repositories.estado_repository import EstadoRepository
from app.schemas.demo import DemoActualizar, DemoCrear, MovimientoDemoActualizar, MovimientoDemoCrear
from app.services.reglas import ReglasNegocio


class DemoService:
    """CRUD de las DEMO y de sus movimientos, más la preparación de una ejecución."""

    def __init__(self, db: Database, reglas: ReglasNegocio, demos: DemoRepository,
                 comandos: ComandoRepository, estados: EstadoRepository):
        self._db = db
        self._reglas = reglas
        self._demos = demos
        self._comandos = comandos
        self._estados = estados

    # --- DEMO ---
    def listar(self, id_vehiculo: int) -> list[dict]:
        with self._db.transaccion() as sesion:
            self._reglas.vehiculo(sesion, id_vehiculo)
            return self._demos.listar_por_vehiculo(sesion, id_vehiculo)

    def crear(self, id_vehiculo: int, datos: DemoCrear) -> int:
        with self._db.transaccion() as sesion:
            self._reglas.vehiculo(sesion, id_vehiculo)
            return self._demos.crear(sesion, id_vehiculo, datos.nombre, datos.descripcion)

    def actualizar(self, id_vehiculo: int, id_demo: int, cambios: DemoActualizar) -> dict:
        with self._db.transaccion() as sesion:
            actual = self._reglas.demo_del_vehiculo(sesion, id_vehiculo, id_demo)
            nuevo = {**actual, **cambios.model_dump(exclude_unset=True)}
            self._demos.actualizar(sesion, id_demo, nuevo["nombre"], nuevo["descripcion"], bool(nuevo["activo"]))
            return self._reglas.demo_del_vehiculo(sesion, id_vehiculo, id_demo)

    def eliminar(self, id_vehiculo: int, id_demo: int) -> None:
        with self._db.transaccion() as sesion:
            self._reglas.demo_del_vehiculo(sesion, id_vehiculo, id_demo)
            self._demos.eliminar(sesion, id_demo)

    # --- Movimientos de la DEMO ---
    def listar_movimientos(self, id_vehiculo: int, id_demo: int) -> list[dict]:
        with self._db.transaccion() as sesion:
            self._reglas.demo_del_vehiculo(sesion, id_vehiculo, id_demo)
            return self._demos.listar_movimientos(sesion, id_demo)

    def agregar_movimiento(self, id_vehiculo: int, id_demo: int, datos: MovimientoDemoCrear) -> list[dict]:
        with self._db.transaccion() as sesion:
            self._reglas.demo_del_vehiculo(sesion, id_vehiculo, id_demo)
            self._reglas.comando_del_vehiculo(sesion, id_vehiculo, datos.id_comando)
            self._demos.agregar_movimiento(sesion, id_demo, datos.id_comando, datos.orden,
                                           datos.duracion_ms, datos.pausa_ms)
            return self._demos.listar_movimientos(sesion, id_demo)

    def actualizar_movimiento(self, id_vehiculo: int, id_demo: int, id_demo_movimiento: int,
                              cambios: MovimientoDemoActualizar) -> list[dict]:
        with self._db.transaccion() as sesion:
            self._reglas.demo_del_vehiculo(sesion, id_vehiculo, id_demo)
            actual = self._reglas.movimiento_de_demo(sesion, id_demo, id_demo_movimiento)
            nuevo = {**actual, **cambios.model_dump(exclude_unset=True)}
            if cambios.id_comando is not None:
                self._reglas.comando_del_vehiculo(sesion, id_vehiculo, cambios.id_comando)
            self._demos.actualizar_movimiento(sesion, id_demo_movimiento, nuevo["id_comando"], nuevo["orden"],
                                              nuevo["duracion_ms"], nuevo["pausa_ms"])
            return self._demos.listar_movimientos(sesion, id_demo)

    def eliminar_movimiento(self, id_vehiculo: int, id_demo: int, id_demo_movimiento: int) -> None:
        with self._db.transaccion() as sesion:
            self._reglas.demo_del_vehiculo(sesion, id_vehiculo, id_demo)
            self._reglas.movimiento_de_demo(sesion, id_demo, id_demo_movimiento)
            self._demos.eliminar_movimiento(sesion, id_demo_movimiento)

    # --- Ejecución ---
    def preparar_ejecucion(self, id_vehiculo: int, id_demo: int) -> dict:
        """Valida la DEMO y lee de RDS sus N movimientos (no hay secuencia fija en el código)."""
        with self._db.transaccion() as sesion:
            self._reglas.vehiculo_activo(sesion, id_vehiculo)
            demo = self._reglas.demo_del_vehiculo(sesion, id_vehiculo, id_demo)
            if not demo["activo"]:
                raise Conflicto(f"La DEMO {id_demo} está inactiva")

            movimientos = self._demos.listar_movimientos(sesion, id_demo)
            if not movimientos:
                raise Conflicto(f"La DEMO {id_demo} no tiene movimientos registrados")

            comandos = {c["id_comando"]: c for c in self._comandos.listar_por_vehiculo(sesion, id_vehiculo)}
            inactivos = [m["comando"] for m in movimientos if not comandos.get(m["id_comando"], {}).get("activo")]
            if inactivos:
                raise Conflicto(f"La DEMO usa comandos inactivos: {', '.join(inactivos)}")

            estado = self._estados.obtener(sesion, id_vehiculo)
            detener = next((c for c in comandos.values() if c["nombre"] == "DETENER" and c["activo"]), None)

        return {
            "demo": demo,
            "movimientos": movimientos,
            # Se conserva lo que haya en RDS: recibir un POST no prueba que el ESP32 esté conectado.
            "conectado": bool(estado["conectado"]) if estado else False,
            "detener": detener,
        }

    def actualizar_estado(self, id_vehiculo: int, id_comando: int, conectado: bool) -> None:
        """Durante la DEMO solo se actualiza el estado; nunca se llama a sp_registrar_historial."""
        with self._db.transaccion() as sesion:
            self._estados.actualizar(sesion, id_vehiculo, id_comando, conectado)
