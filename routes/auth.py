from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required

from models import Usuario

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        usuario = request.form.get("usuario")
        password = request.form.get("password")

        user = Usuario.query.filter_by(
            usuario=usuario,
            activo=True
        ).first()

        if user and user.check_password(password):
            login_user(user)

            # ==========================================
            # Obligar cambio de contraseña
            # ==========================================

            if user.cambiar_password:
                flash(
                    "Debe cambiar su contraseña antes de continuar.",
                    "warning"
                )
                return redirect(
                    url_for("auth.cambiar_password")
                )

            return redirect(
                url_for("dashboard")
            )

        flash("Usuario o contraseña incorrectos.", "danger")

    return render_template("login.html"
    )

# ==========================================
# CAMBIAR CONTRASEÑA
# ==========================================

@auth.route(
    "/cambiar_password",
    methods=["GET", "POST"]
)
@login_required
def cambiar_password():

    from flask_login import current_user
    from models import db

    if request.method == "POST":

        actual = request.form["actual"]

        nueva = request.form["nueva"]

        confirmar = request.form["confirmar"]

        if not current_user.check_password(actual):

            flash(
                "La contraseña actual es incorrecta.",
                "danger"
            )

            return redirect(
                url_for("auth.cambiar_password")
            )

        if nueva != confirmar:

            flash(
                "Las nuevas contraseñas no coinciden.",
                "danger"
            )

            return redirect(
                url_for("auth.cambiar_password")
            )

        current_user.set_password(nueva)

        current_user.cambiar_password = False

        db.session.commit()

        flash(
            "Contraseña actualizada correctamente.",
            "success"
        )

        return redirect(
            url_for("dashboard")
        )

    return render_template(
        "cambiar_password.html"
    )


@auth.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(url_for("auth.login"))