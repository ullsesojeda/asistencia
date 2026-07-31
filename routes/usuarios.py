from flask import Blueprint, render_template, request, redirect, url_for, flash
import secrets
import string
from flask_login import login_required
from utils.permisos import admin_required
from models import db, Usuario, Empleado
usuarios=Blueprint("usuarios",__name__)
# =====================================================
# GENERAR CONTRASEÑA TEMPORAL
# =====================================================

def generar_password(longitud=8):

    caracteres = (
        string.ascii_letters +
        string.digits
    )

    return "".join(
        secrets.choice(caracteres)
        for _ in range(longitud)
    )
@usuarios.route("/usuarios")
@login_required
@admin_required
def lista_usuarios():
    return render_template("usuarios.html",usuarios=Usuario.query.order_by(Usuario.nombre).all())
@usuarios.route("/usuarios/editar/<int:id>",methods=["POST"])
@login_required
@admin_required
def editar_usuario(id):
    u=Usuario.query.get_or_404(id)
    u.nombre=request.form["nombre"].strip()
    u.rol=request.form["rol"]
    db.session.commit()
    flash("Usuario actualizado.","success")
    return redirect(url_for("usuarios.lista_usuarios"))
@usuarios.route("/usuarios/estado/<int:id>")
@login_required
@admin_required
def cambiar_estado(id):
    u=Usuario.query.get_or_404(id)
    if u.usuario!="admin":
        u.activo=not u.activo
        db.session.commit()
    return redirect(url_for("usuarios.lista_usuarios"))
# =====================================================
# RESTABLECER CONTRASEÑA
# =====================================================

@usuarios.route("/usuarios/restablecer_password/<int:id>")
@login_required
@admin_required
def restablecer_password(id):

    usuario = Usuario.query.get_or_404(id)

    # No permitir restablecer al administrador principal
    if usuario.usuario == "admin":

        flash(
            "No es posible restablecer la contraseña del administrador principal.",
            "warning"
        )

        return redirect(
            url_for("usuarios.lista_usuarios")
        )

    # Si es un empleado
    if usuario.empleado:

        password_temporal = usuario.empleado.numero_empleado

    else:

        password_temporal = "Admin123"

    usuario.set_password(password_temporal)

    usuario.cambiar_password = True

    db.session.commit()

    flash(

        f"Contraseña restablecida correctamente.\n"
        f"Contraseña temporal: {password_temporal}",

        "success"

    )

    return redirect(
        url_for("usuarios.lista_usuarios")
    )

# =====================================================
# NUEVO USUARIO
# =====================================================

@usuarios.route("/usuarios/nuevo", methods=["POST"])
@login_required
@admin_required
def nuevo_usuario():

    usuario = request.form["usuario"].strip()

    nombre = request.form["nombre"].strip()

    rol = request.form["rol"]

    # ==========================================
    # VALIDACIONES
    # ==========================================

    if not usuario:

        flash(
            "Debe capturar un nombre de usuario.",
            "danger"
        )

        return redirect(
            url_for("usuarios.lista_usuarios")
        )

    if not nombre:

        flash(
            "Debe capturar el nombre del usuario.",
            "danger"
        )

        return redirect(
            url_for("usuarios.lista_usuarios")
        )

    usuario = usuario.lower()

    # Verificar si ya existe
    if Usuario.query.filter_by(usuario=usuario).first():

        flash(
            "Ese nombre de usuario ya existe.",
            "danger"
        )

        return redirect(
            url_for("usuarios.lista_usuarios")
        )

    password_temporal = generar_password()

    nuevo = Usuario(

        usuario=usuario,

        nombre=nombre,

        rol=rol,

        activo=True,

        cambiar_password=True

    )

    nuevo.set_password(password_temporal)

    db.session.add(nuevo)

    db.session.commit()

    flash(

    f"""
Usuario creado correctamente.

Usuario:
{usuario}

Contraseña temporal:
{password_temporal}

El usuario deberá cambiar su contraseña al iniciar sesión.
""",

    "success"

)
    return redirect(
        url_for("usuarios.lista_usuarios")
    )
