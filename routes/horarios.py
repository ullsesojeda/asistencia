from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from models import db, Horario

from datetime import datetime

from utils.permisos import admin_required

horarios = Blueprint("horarios", __name__)


# ==========================================================
# GENERAR CLAVE AUTOMÁTICA
# ==========================================================
def generar_clave_horario():

    ultimo = Horario.query.order_by(Horario.id.desc()).first()

    if ultimo:
        numero = int(ultimo.clave.split("-")[1]) + 1
    else:
        numero = 1

    return f"HOR-{numero:04d}"


# ==========================================================
# LISTA
# ==========================================================
@horarios.route("/horarios")
@login_required
@admin_required
def lista_horarios():

    lista = Horario.query.order_by(Horario.nombre).all()

    return render_template(
        "horarios.html",
        horarios=lista
    )


# ==========================================================
# NUEVO
# ==========================================================
@horarios.route("/horarios/nuevo", methods=["POST"])
@login_required
@admin_required
def nuevo_horario():

    nuevo = Horario(

        clave=generar_clave_horario(),

        nombre=request.form["nombre"],

        hora_entrada=datetime.strptime(
    request.form["hora_entrada"],
    "%H:%M"
).time(),

hora_salida=datetime.strptime(
    request.form["hora_salida"],
    "%H:%M"
).time(),

        tolerancia=request.form["tolerancia"],

        observaciones=request.form["observaciones"],

        activo=True

    )

    db.session.add(nuevo)
    db.session.commit()

    flash(
        "Horario registrado correctamente.",
        "success"
    )

    return redirect(
        url_for("horarios.lista_horarios")
    )


# ==========================================================
# EDITAR
# ==========================================================

@horarios.route("/horarios/editar/<int:id>", methods=["POST"])
@login_required
@admin_required
def editar_horario(id):

    horario = Horario.query.get_or_404(id)

    horario.nombre = request.form["nombre"]

    horario.hora_entrada = datetime.strptime(
        request.form["hora_entrada"],
        "%H:%M"
    ).time()

    horario.hora_salida = datetime.strptime(
        request.form["hora_salida"],
        "%H:%M"
    ).time()

    horario.tolerancia = int(request.form["tolerancia"])

    horario.observaciones = request.form["observaciones"]

    db.session.commit()

    flash(
        "Horario actualizado correctamente.",
        "success"
    )

    return redirect(
        url_for("horarios.lista_horarios")
    )

# ==========================================================
# ACTIVAR / INACTIVAR
# ==========================================================
@horarios.route("/horarios/estado/<int:id>")
@login_required
@admin_required
def cambiar_estado_horario(id):

    horario = Horario.query.get_or_404(id)

    horario.activo = not horario.activo

    db.session.commit()

    flash(
        "Estado del horario actualizado.",
        "success"
    )

    return redirect(
        url_for("horarios.lista_horarios")
    )