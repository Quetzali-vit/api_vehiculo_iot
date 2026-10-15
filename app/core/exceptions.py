class ApiError(Exception):
    """Error de negocio que se traduce a una respuesta HTTP controlada."""

    status_code = 500

    def __init__(self, mensaje: str):
        super().__init__(mensaje)
        self.mensaje = mensaje


class SolicitudInvalida(ApiError):
    status_code = 400


class NoEncontrado(ApiError):
    status_code = 404


class Conflicto(ApiError):
    status_code = 409


class BaseDatosNoDisponible(ApiError):
    status_code = 503
