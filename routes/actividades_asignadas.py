from datetime import datetime, date

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import (
    login_required
)

from models import (
    db,
    ActividadAsignada,
    Actividad,
    Empleado
)

from utils.permisos import admin_required


actividades_asignadas = Blueprint(
    "actividades_asignadas",
    __name__
)
# ======================================================
# LISTADO
# ======================================================

@actividades_asignadas.route("/actividades_asignadas")
@login_required
@admin_required
def lista():

    actividades = (
        ActividadAsignada.query
        .order_by(
            ActividadAsignada.fecha_programada.desc(),
            ActividadAsignada.id.desc()
        )
        .all()
    )

    actividades_realizadas = (
        Actividad.query
        .join(Empleado)
        .order_by(
            Actividad.fecha.desc(),
            Actividad.hora_inicio.desc()
        )
        .all()
    )

    empleados = (
        Empleado.query
        .filter_by(activo=True)
        .order_by(
            Empleado.nombre,
            Empleado.apellido_paterno
        )
        .all()
    )

    return render_template(

        "actividades_asignadas.html",

        actividades=actividades,

        actividades_realizadas=actividades_realizadas,

        empleados=empleados,

        hoy=date.today()

    )
# ======================================================
# NUEVA ACTIVIDAD
# ======================================================

@actividades_asignadas.route(
    "/actividades_asignadas/nueva",
    methods=["POST"]
)
@login_required
@admin_required
def nueva():

    try:

        actividad = ActividadAsignada(

            empleado_id=int(
                request.form["empleado_id"]
            ),

            actividad=request.form["actividad"],

            descripcion=request.form["descripcion"],

            fecha_programada=datetime.strptime(
                request.form["fecha_programada"],
                "%Y-%m-%d"
            ).date(),

            prioridad=request.form["prioridad"],

            observaciones=request.form["observaciones"],

            estado="Pendiente"

        )

        db.session.add(actividad)

        db.session.commit()

        flash(
            "Actividad asignada correctamente.",
            "success"
        )

    except Exception as e:

        db.session.rollback()

        flash(
            f"Error: {e}",
            "danger"
        )

    return redirect(
        url_for(
            "actividades_asignadas.lista"
        )
    )