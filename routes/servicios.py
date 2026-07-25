from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from models import db, Servicio
from utils.permisos import admin_required

servicios = Blueprint("servicios", __name__)


# ==========================================================
# GENERAR CLAVE AUTOMÁTICA
# ==========================================================
def generar_clave_servicio():

    ultimo = Servicio.query.order_by(Servicio.id.desc()).first()

    if ultimo:

        numero = int(ultimo.clave.split("-")[1]) + 1

    else:

        numero = 1

    return f"SER-{numero:04d}"


# ==========================================================
# LISTA DE SERVICIOS
# ==========================================================
@servicios.route("/servicios")
@login_required
@admin_required
def lista_servicios():

    lista = Servicio.query.order_by(
        Servicio.nombre
    ).all()

    return render_template(
        "servicios.html",
        servicios=lista
    )


# ==========================================================
# NUEVO SERVICIO
# ==========================================================
@servicios.route("/servicios/nuevo", methods=["POST"])
@login_required
@admin_required
def nuevo_servicio():

    nuevo = Servicio(

        clave=generar_clave_servicio(),

        nombre=request.form["nombre"],

        cliente=request.form["cliente"],

        direccion=request.form["direccion"],

        telefono=request.form["telefono"],

        observaciones=request.form["observaciones"],

        activo=True

    )

    db.session.add(nuevo)

    db.session.commit()

    flash(
        "Servicio registrado correctamente.",
        "success"
    )

    return redirect(
        url_for("servicios.lista_servicios")
    )
# ==========================================================
# EDITAR SERVICIO
# ==========================================================
@servicios.route("/servicios/editar/<int:id>", methods=["POST"])
@login_required
@admin_required
def editar_servicio(id):

    servicio = Servicio.query.get_or_404(id)

    servicio.nombre = request.form["nombre"]
    servicio.cliente = request.form["cliente"]
    servicio.direccion = request.form["direccion"]
    servicio.telefono = request.form["telefono"]
    servicio.observaciones = request.form["observaciones"]

    db.session.commit()

    flash(
        "Servicio actualizado correctamente.",
        "success"
    )

    return redirect(
        url_for("servicios.lista_servicios")
    )
# ==========================================================
# ACTIVAR / INACTIVAR
# ==========================================================
@servicios.route("/servicios/estado/<int:id>")
@login_required
@admin_required
def cambiar_estado_servicio(id):

    servicio = Servicio.query.get_or_404(id)

    servicio.activo = not servicio.activo

    db.session.commit()

    flash(
        "Estado del servicio actualizado.",
        "success"
    )

    return redirect(
        url_for("servicios.lista_servicios")
    )