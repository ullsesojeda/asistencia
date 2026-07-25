from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager, login_required

from config import Config
from models import db, Usuario

from routes.auth import auth

from routes.usuarios import usuarios

from routes.empleados import empleados

from routes.servicios import servicios

from routes.horarios import horarios

from routes.asignaciones import asignaciones

from routes.asistencias import asistencias

app = Flask(__name__)
app.config.from_object(Config)

# ==========================================
# Base de Datos
# ==========================================
db.init_app(app)

# ==========================================
# Login
# ==========================================
login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = "auth.login"
login_manager.login_message = "Debe iniciar sesión."
login_manager.login_message_category = "warning"

# Registrar Blueprints
app.register_blueprint(auth)
app.register_blueprint(usuarios)
app.register_blueprint(empleados)
app.register_blueprint(servicios)
app.register_blueprint(horarios)
app.register_blueprint(asignaciones)
app.register_blueprint(asistencias)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Usuario, int(user_id))


# ==========================================
# Rutas
# ==========================================
@app.route("/")
def inicio():
    return redirect(url_for("auth.login"))

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


# ==========================================
# Crear Administrador
# ==========================================
def crear_admin():

    if not Usuario.query.filter_by(usuario="admin").first():

        admin = Usuario(
            usuario="admin",
            nombre="Administrador",
            rol="Administrador"
        )

        admin.set_password("admin123")

        db.session.add(admin)
        db.session.commit()

        print("===================================")
        print("Administrador creado correctamente")
        print("Usuario : admin")
        print("Password: admin123")
        print("===================================")


# ==========================================
# Inicio
# ==========================================
if __name__ == "__main__":

    with app.app_context():

        db.create_all()

        crear_admin()

    app.run(
    host="0.0.0.0",
    port=5000,
    debug=True
    )