from datetime import datetime

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import (
    login_required,
    current_user
)

from models import (
    db,
    Actividad,
    ActividadAsignada,
    Empleado
)

actividades = Blueprint(
    "actividades",
    __name__,
    url_prefix="/actividades"
)


# ===========================================
# MIS ACTIVIDADES
# ===========================================

@actividades.route("/")
@login_required
def lista():

    empleado = current_user.empleado

    actividades = Actividad.query.filter_by(
        empleado_id=empleado.id
    ).order_by(
        Actividad.id.desc()
    ).all()

    pendientes = ActividadAsignada.query.filter_by(
        empleado_id=empleado.id,
        estado="Pendiente"
    ).order_by(
        ActividadAsignada.fecha_programada
    ).all()

    return render_template(
        "actividades.html",
        actividades=actividades,
        pendientes=pendientes
    )

# ===========================================
# NUEVA ACTIVIDAD
# ===========================================

@actividades.route("/nueva", methods=["GET", "POST"])
@login_required
def nueva():

    if request.method == "POST":

        actividad = Actividad(

            empleado_id=current_user.empleado.id,

            actividad=request.form["actividad"],

            descripcion=request.form["descripcion"],

            hora_inicio=datetime.now(),

            estado="En proceso"

        )

        db.session.add(actividad)

        db.session.commit()

        flash(
            "Actividad iniciada correctamente.",
            "success"
        )

        return redirect(
            url_for("actividades.lista")
        )

    return render_template(
        "actividad_nueva.html"
    )


# ===========================================
# FINALIZAR
# ===========================================

@actividades.route("/finalizar/<int:id>")
@login_required
def finalizar(id):

    actividad = Actividad.query.get_or_404(id)

    if actividad.empleado_id != current_user.empleado.id:

        flash(
            "No tiene permiso.",
            "danger"
        )

        return redirect(
            url_for("actividades.lista")
        )

    actividad.hora_fin = datetime.now()

    actividad.estado = "Terminada"

    asignada = ActividadAsignada.query.filter_by(
    empleado_id=actividad.empleado_id,
    actividad=actividad.actividad,
    estado="En proceso"
    ).first()

    if asignada:
        asignada.estado = "Terminada"

    db.session.commit()

    flash(
        "Actividad finalizada.",
        "success"
    )

    return redirect(
        url_for("actividades.lista")
    )
@actividades.route("/iniciar_asignada/<int:id>")
@login_required
def iniciar_asignada(id):

    asignada = ActividadAsignada.query.get_or_404(id)

    if asignada.empleado_id != current_user.empleado.id:

        flash(
            "No tiene permiso para iniciar esta actividad.",
            "danger"
        )

        return redirect(
            url_for("actividades.lista")
        )

    if asignada.estado != "Pendiente":

        flash(
            "La actividad ya fue iniciada.",
            "warning"
        )

        return redirect(
            url_for("actividades.lista")
        )

    actividad = Actividad(

        empleado_id=current_user.empleado.id,

        actividad=asignada.actividad,

        descripcion=asignada.descripcion,

        hora_inicio=datetime.now(),

        estado="En proceso"

    )

    db.session.add(actividad)

    asignada.estado = "En proceso"

    db.session.commit()

    flash(
        "Actividad iniciada correctamente.",
        "success"
    )

    return redirect(
        url_for("actividades.lista")
    )
# ===========================================
# ACTIVIDADES ASIGNADAS (ADMIN)
# ===========================================

@actividades.route("/asignadas")
@login_required
def lista_asignadas():

    if current_user.rol != "Administrador":

        flash(
            "No tiene permiso para acceder a este módulo.",
            "danger"
        )

        return redirect(url_for("dashboard"))

    actividades = ActividadAsignada.query.order_by(
        ActividadAsignada.fecha_programada.desc()
    ).all()

    return render_template(
        "actividades_asignadas.html",
        actividades=actividades
    )