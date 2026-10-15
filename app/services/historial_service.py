from app.db.database import Database
from app.repositories.historial_repository import HistorialRepository
from app.services.reglas import ReglasNegocio


class HistorialService:
    LIMITE_MAXIMO = 10

    def __init__(self, db: Database, reglas: ReglasNegocio, historial: HistorialRepository):
        self._db = db
        self._reglas = reglas
        self._historial = historial

    def ultimos(self, id_vehiculo: int, limite: int = LIMITE_MAXIMO) -> dict:
        """Hasta 10 movimientos individuales, del más reciente al más antiguo.

        El SP ya los devuelve ordenados por fecha descendente; aquí solo se recorta la lista,
        así que el historial completo se conserva en RDS.
        """
        limite = min(limite, self.LIMITE_MAXIMO)
        with self._db.transaccion() as sesion:
            self._reglas.vehiculo(sesion, id_vehiculo)
            registros = self._historial.obtener(sesion, id_vehiculo)
        visibles = registros[:limite]
        return {
            "id_vehiculo": id_vehiculo,
            "limite": limite,
            "total_registrados": len(registros),
            "devueltos": len(visibles),
            "movimientos": visibles,
        }
