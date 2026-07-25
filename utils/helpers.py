import re
import unicodedata

from models import Empleado, Usuario


# ==========================================================
# GENERAR NÚMERO DE EMPLEADO
# ==========================================================
def generar_numero_empleado():
    """
    Genera el siguiente número consecutivo:
    EMP-0001
    EMP-0002
    """

    ultimo = (
        Empleado.query
        .order_by(Empleado.id.desc())
        .first()
    )

    if not ultimo:
        return "EMP-0001"

    try:
        consecutivo = int(
            ultimo.numero_empleado.replace("EMP-", "")
        )
    except (ValueError, AttributeError):
        consecutivo = ultimo.id

    consecutivo += 1

    return f"EMP-{consecutivo:04d}"


# ==========================================================
# LIMPIAR TEXTO
# ==========================================================
def limpiar_texto(texto):
    """
    Elimina acentos, espacios y caracteres especiales.
    """

    texto = texto.strip().lower()

    texto = unicodedata.normalize("NFKD", texto)
    texto = texto.encode("ascii", "ignore").decode("utf-8")

    texto = re.sub(r"[^a-z0-9]", "", texto)

    return texto


# ==========================================================
# GENERAR USUARIO
# ==========================================================
def generar_usuario(nombre, apellido_paterno):
    """
    Genera un usuario automáticamente.

    Ejemplos:

    Juan Pérez
        -> jperez

    Carlos Mendoza
        -> cmendoza

    Si existe:
        jperez

    genera:

        jperez1
        jperez2
    """

    inicial = limpiar_texto(nombre)[0]

    apellido = limpiar_texto(apellido_paterno)

    base = f"{inicial}{apellido}"

    usuario = base

    contador = 1

    while Usuario.query.filter_by(usuario=usuario).first():

        usuario = f"{base}{contador}"

        contador += 1

    return usuario