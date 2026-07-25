from datetime import datetime, date

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from models import (
    db,
    Asignacion,
    Empleado,
    Servicio,
    Horario
)
from utils.permisos import admin_required

asignaciones = Blueprint("asignaciones", __name__)

@asignaciones.route("/asignaciones")
@login_required
@admin_required
def lista_asignaciones():

    lista = Asignacion.query.order_by(
        Asignacion.id.desc()
    ).all()

    empleados = Empleado.query.filter_by(
        activo=True
    ).order_by(
        Empleado.nombre
    ).all()

    servicios = Servicio.query.filter_by(
        activo=True
    ).order_by(
        Servicio.nombre
    ).all()

    horarios = Horario.query.filter_by(
        activo=True
    ).order_by(
        Horario.nombre
    ).all()

    return render_template(
        "asignaciones.html",
        asignaciones=lista,
        empleados=empleados,
        servicios=servicios,
        horarios=horarios,
        hoy=date.today()
    )

@asignaciones.route("/asignaciones/nueva", methods=["POST"])
@login_required
@admin_required
def nueva_asignacion():

    empleado_id = int(request.form["empleado_id"])

    servicio_id = int(request.form["servicio_id"])

    horario_id = int(request.form["horario_id"])

    fecha_inicio = datetime.strptime(
        request.form["fecha_inicio"],
        "%Y-%m-%d"
    ).date()


    # Buscar asignación activa del empleado

    anterior = Asignacion.query.filter_by(
        empleado_id=empleado_id,
        activo=True
    ).first()


    if anterior:

        anterior.activo = False

        anterior.fecha_fin = fecha_inicio


    nueva = Asignacion(

        empleado_id=empleado_id,

        servicio_id=servicio_id,

        horario_id=horario_id,

        fecha_inicio=fecha_inicio,

        activo=True

    )

    db.session.add(nueva)

    db.session.commit()

    flash(
        "Asignación registrada correctamente.",
        "success"
    )

    return redirect(
        url_for("asignaciones.lista_asignaciones")
    )