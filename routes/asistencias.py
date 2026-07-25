from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    current_app
)

from flask_login import login_required, current_user

from werkzeug.utils import secure_filename

from datetime import datetime
import os
import uuid

from models import (
    db,
    Asistencia,
    Asignacion
)
from utils.permisos import admin_required

asistencias = Blueprint(
    "asistencias",
    __name__,
    url_prefix="/asistencias"
)


# ==========================================================
# OBTENER ASIGNACIÓN ACTIVA
# ==========================================================

def obtener_asignacion_activa(empleado_id):

    return Asignacion.query.filter_by(
        empleado_id=empleado_id,
        activo=True
    ).first()


# ==========================================================
# DETERMINAR SI CORRESPONDE ENTRADA O SALIDA
# ==========================================================

def obtener_siguiente_movimiento(empleado_id):

    hoy = datetime.now().date()

    registros = (
        Asistencia.query
        .filter(
            Asistencia.empleado_id == empleado_id,
            db.func.date(Asistencia.fecha_hora) == hoy
        )
        .order_by(Asistencia.fecha_hora.asc())
        .all()
    )

    if len(registros) == 0:
        return "Entrada"

    if len(registros) == 1:
        return "Salida"

    return "Completado"


# ==========================================================
# PANTALLA PRINCIPAL
# ==========================================================

@asistencias.route("/")
@login_required
def mi_asistencia():

    if current_user.empleado is None:

        flash(
            "Este usuario no tiene un empleado asignado.",
            "warning"
        )

        return redirect(url_for("dashboard"))

    asignacion = obtener_asignacion_activa(
        current_user.empleado.id
    )

    if asignacion is None:

        flash(
            "No existe una asignación activa.",
            "warning"
        )

        return redirect(url_for("dashboard"))

    siguiente = obtener_siguiente_movimiento(
        current_user.empleado.id
    )

    return render_template(

        "asistencias.html",

        empleado=current_user.empleado,

        servicio=asignacion.servicio,

        horario=asignacion.horario,

        siguiente=siguiente

    )
# ==========================================================
# REGISTRAR ASISTENCIA
# ==========================================================

@asistencias.route("/registrar", methods=["POST"])
@login_required
def registrar_asistencia():

    if current_user.empleado is None:

        flash(
            "Este usuario no tiene un empleado asignado.",
            "danger"
        )

        return redirect(url_for("asistencias.mi_asistencia"))

    asignacion = obtener_asignacion_activa(
        current_user.empleado.id
    )

    if asignacion is None:

        flash(
            "No existe una asignación activa.",
            "warning"
        )

        return redirect(url_for("asistencias.mi_asistencia"))

    movimiento = obtener_siguiente_movimiento(
        current_user.empleado.id
    )

    if movimiento == "Completado":

        flash(
            "La asistencia del día ya fue registrada.",
            "info"
        )

        return redirect(url_for("asistencias.mi_asistencia"))

    # ======================================================
    # DATOS RECIBIDOS
    # ======================================================

    latitud = request.form.get("latitud")
    longitud = request.form.get("longitud")
    precision = request.form.get("precision")
    direccion = request.form.get("direccion")
    observaciones = request.form.get("observaciones", "")

    # ======================================================
    # FOTOGRAFÍA
    # ======================================================

    foto = request.files.get("foto")

    ruta_foto = None

    if foto and foto.filename != "":

        extension = os.path.splitext(
            secure_filename(foto.filename)
        )[1].lower()

        if extension == "":
            extension = ".jpg"

        nombre_archivo = (
            f"{uuid.uuid4().hex}{extension}"
        )

        carpeta = os.path.join(
            current_app.root_path,
            "static",
            "uploads",
            "asistencias"
        )

        os.makedirs(carpeta, exist_ok=True)

        ruta_completa = os.path.join(
            carpeta,
            nombre_archivo
        )

        foto.save(ruta_completa)

        ruta_foto = (
            f"uploads/asistencias/{nombre_archivo}"
        )

    # ======================================================
    # INFORMACIÓN DEL DISPOSITIVO
    # ======================================================

    ip = request.remote_addr

    navegador = request.user_agent.string

    dispositivo = request.user_agent.platform

    # ======================================================
    # CREAR REGISTRO
    # ======================================================

    asistencia = Asistencia(

        empleado_id=current_user.empleado.id,

        servicio_id=asignacion.servicio_id,

        horario_id=asignacion.horario_id,

        fecha_hora=datetime.now(),

        tipo=movimiento,

        estatus="Registrado",

        latitud=latitud,

        longitud=longitud,

        precision=precision,

        direccion=direccion,

        foto=ruta_foto,

        ip=ip,

        dispositivo=dispositivo,

        navegador=navegador,

        observaciones=observaciones

    )

    db.session.add(asistencia)

    db.session.commit()

    flash(
        f"{movimiento} registrada correctamente.",
        "success"
    )

    return redirect(
        url_for("asistencias.mi_asistencia")
    )
# ==========================================================
# HISTORIAL DE ASISTENCIAS
# ==========================================================

@asistencias.route("/historial")
@login_required
@admin_required
def historial():

    if current_user.rol == "Administrador":

        registros = (
            Asistencia.query
            .order_by(Asistencia.fecha_hora.desc())
            .all()
        )

    else:

        if current_user.empleado is None:

            flash(
                "Este usuario no tiene un empleado asignado.",
                "warning"
            )

            return redirect(url_for("dashboard"))

        registros = (
            Asistencia.query
            .filter_by(
                empleado_id=current_user.empleado.id
            )
            .order_by(Asistencia.fecha_hora.desc())
            .all()
        )

    return render_template(
        "historial_asistencias.html",
        registros=registros
    )
# ==========================================================
# VER FOTOGRAFÍA
# ==========================================================

@asistencias.route("/foto/<int:id>")
@login_required
@admin_required
def ver_foto(id):

    asistencia = Asistencia.query.get_or_404(id)

    return render_template(
        "foto_asistencia.html",
        asistencia=asistencia
    )
# ==========================================================
# VER UBICACIÓN
# ==========================================================

@asistencias.route("/ubicacion/<int:id>")
@login_required
@admin_required
def ver_ubicacion(id):

    asistencia = Asistencia.query.get_or_404(id)

    if not asistencia.latitud or not asistencia.longitud:

        flash(
            "Esta asistencia no tiene ubicación registrada.",
            "warning"
        )

        return redirect(
            url_for("asistencias.historial")
        )

    return redirect(
        f"https://www.google.com/maps?q={asistencia.latitud},{asistencia.longitud}"
    )