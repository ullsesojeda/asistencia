from flask import Blueprint,render_template,request,redirect,url_for,flash
from flask_login import login_required
from utils.permisos import admin_required
from models import db,Usuario
usuarios=Blueprint("usuarios",__name__)
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
