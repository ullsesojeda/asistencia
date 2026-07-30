from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from models import db, Empleado, Usuario
from utils.helpers import generar_numero_empleado, generar_usuario
from utils.permisos import admin_required

empleados = Blueprint("empleados", __name__)


@empleados.route("/empleados")
@login_required
@admin_required

def lista_empleados():
    lista = Empleado.query.order_by(
        Empleado.nombre,
        Empleado.apellido_paterno
    ).all()

    return render_template("empleados.html", empleados=lista)


@empleados.route("/empleados/nuevo", methods=["POST"])
@login_required
@admin_required
def nuevo_empleado():

    try:

        nombre = request.form["nombre"].strip()
        apellido_paterno = request.form["apellido_paterno"].strip()
        apellido_materno = request.form.get("apellido_materno", "").strip()
        puesto = request.form["puesto"].strip()
        telefono = request.form.get("telefono", "").strip()
        correo = request.form.get("correo", "").strip()
        hora_entrada = (
            datetime.strptime(
                request.form["hora_entrada"],
                "%H:%M"
            ).time()
            if request.form["hora_entrada"]
            else None
        )

        hora_salida = (
            datetime.strptime(
                request.form["hora_salida"],
                "%H:%M"
            ).time()
            if request.form["hora_salida"]
            else None
        )

        turno = request.form["turno"]
        dias_descanso = request.form["dias_descanso"]
        departamento = request.form["departamento"]
        jefe_inmediato = request.form["jefe_inmediato"]

        numero = generar_numero_empleado()

        usuario_generado = generar_usuario(
            nombre,
            apellido_paterno
        )

        # Evitar usuarios duplicados
        contador = 1
        usuario_base = usuario_generado

        while Usuario.query.filter_by(usuario=usuario_generado).first():
            usuario_generado = f"{usuario_base}{contador}"
            contador += 1

        empleado = Empleado(
            numero_empleado=numero,
            nombre=nombre,
            apellido_paterno=apellido_paterno,
            apellido_materno=apellido_materno,
            puesto=puesto,
            telefono=telefono,
            correo=correo,
            hora_entrada=hora_entrada,
            hora_salida=hora_salida,
            turno=turno,
            dias_descanso=dias_descanso,
            departamento=departamento,
            jefe_inmediato=jefe_inmediato,
            fecha_ingreso=datetime.today().date()
        )

        db.session.add(empleado)

        db.session.flush()

        usuario = Usuario(

            usuario=usuario_generado,

            nombre=empleado.nombre_completo(),

            rol="Empleado",

            empleado_id=empleado.id,

            cambiar_password=True

        )

        # Contraseña inicial = número de empleado
        usuario.set_password(numero)

        db.session.add(usuario)

        db.session.commit()

        flash(

            f"Empleado registrado correctamente.\n"
            f"Usuario: {usuario_generado}\n"
            f"Contraseña temporal: {numero}",

            "success"

        )

    except Exception as e:

        db.session.rollback()

        flash(f"Error: {e}", "danger")

    return redirect(url_for("empleados.lista_empleados"))

@empleados.route("/empleados/editar/<int:empleado_id>", methods=["POST"])
@login_required
@admin_required
def editar_empleado(empleado_id):
    empleado = Empleado.query.get_or_404(empleado_id)

    try:
        empleado.nombre = request.form["nombre"].strip()
        empleado.apellido_paterno = request.form["apellido_paterno"].strip()
        empleado.apellido_materno = request.form.get("apellido_materno", "").strip()
        empleado.puesto = request.form["puesto"].strip()
        empleado.telefono = request.form.get("telefono", "").strip()
        empleado.correo = request.form.get("correo", "").strip()
        empleado.hora_entrada = (
            datetime.strptime(
                request.form["hora_entrada"],
                "%H:%M"
            ).time()
            if request.form["hora_entrada"]
            else None
    )

        empleado.hora_salida = (
            datetime.strptime(
            request.form["hora_salida"],
            "%H:%M"
            ).time()
            if request.form["hora_salida"]
            else None
    )   

        empleado.turno = request.form.get("turno", "")

        empleado.dias_descanso = request.form.get("dias_descanso", "")

        empleado.departamento = request.form.get("departamento", "")

        empleado.jefe_inmediato = request.form.get("jefe_inmediato", "")

        if empleado.usuario:
            empleado.usuario.nombre = empleado.nombre_completo()

        db.session.commit()
        flash("Empleado actualizado correctamente.", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Error al actualizar: {e}", "danger")

    return redirect(url_for("empleados.lista_empleados"))


@empleados.route("/empleados/estado/<int:empleado_id>")
@login_required
@admin_required
def cambiar_estado(empleado_id):
    empleado = Empleado.query.get_or_404(empleado_id)
    empleado.activo = not empleado.activo

    if empleado.usuario:
        empleado.usuario.activo = empleado.activo

    db.session.commit()
    flash("Estado actualizado correctamente.", "success")

    return redirect(url_for("empleados.lista_empleados"))
