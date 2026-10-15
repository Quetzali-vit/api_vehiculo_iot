from pydantic import BaseModel


class Mensaje(BaseModel):
    mensaje: str


class ErrorRespuesta(BaseModel):
    detail: str


def respuestas_error(*codigos: int) -> dict:
    """Arma el bloque `responses` de Swagger para los códigos de error indicados."""
    descripciones = {
        400: "Solicitud inválida o referencia a un registro inexistente",
        401: "Falta el encabezado X-API-Key",
        403: "La clave X-API-Key no es válida",
        404: "El recurso no existe",
        409: "Conflicto con el estado actual (inactivo, duplicado, DEMO en curso…)",
        503: "Amazon RDS no está disponible",
    }
    return {c: {"model": ErrorRespuesta, "description": descripciones[c]} for c in codigos}
