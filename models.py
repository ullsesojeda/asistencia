from datetime import datetime

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


# ==========================================================
# USUARIOS DEL SISTEMA
# ==========================================================
class Usuario(UserMixin, db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    rol = db.Column(db.String(20), nullable=False, default="Empleado")
    activo = db.Column(db.Boolean, default=True)

     # Nuevo campo
    cambiar_password = db.Column(
        db.Boolean,
        default=True
    )

    empleado_id = db.Column(
        db.Integer,
        db.ForeignKey("empleados.id"),
        nullable=True
    )

    empleado = db.relationship(
    "Empleado",
    back_populates="usuario"
    )

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def __repr__(self):
        return f"<Usuario {self.usuario}>"


# ==========================================================
# EMPLEADOS
# ==========================================================
class Empleado(db.Model):
    __tablename__ = "empleados"

    id = db.Column(db.Integer, primary_key=True)

    # Número generado automáticamente (EMP-0001)
    numero_empleado = db.Column(
        db.String(20),
        unique=True,
        nullable=False
    )

    nombre = db.Column(db.String(80), nullable=False)
    apellido_paterno = db.Column(db.String(80), nullable=False)
    apellido_materno = db.Column(db.String(80))

    puesto = db.Column(db.String(80), nullable=False)

    telefono = db.Column(db.String(20))
    correo = db.Column(db.String(120))

    fecha_ingreso = db.Column(db.Date)

    # Estado laboral
    estatus = db.Column(
        db.String(20),
        default="Activo"
    )

    activo = db.Column(
        db.Boolean,
        default=True
    )

    usuario = db.relationship(
    "Usuario",
    back_populates="empleado",
    uselist=False
)

    asistencias = db.relationship(
        "Asistencia",
        back_populates="empleado",
        cascade="all, delete-orphan"
    )

    def nombre_completo(self):
        return (
            f"{self.nombre} "
            f"{self.apellido_paterno} "
            f"{self.apellido_materno or ''}"
        ).strip()

    def __repr__(self):
        return f"<Empleado {self.numero_empleado}>"

# ==========================================================
# SERVICIOS
# ==========================================================
class Servicio(db.Model):
    __tablename__ = "servicios"

    id = db.Column(db.Integer, primary_key=True)

    # Clave automática (SER-0001)
    clave = db.Column(
        db.String(20),
        unique=True,
        nullable=False
    )

    nombre = db.Column(
        db.String(100),
        nullable=False
    )

    cliente = db.Column(
        db.String(120)
    )

    direccion = db.Column(
        db.String(250)
    )

    telefono = db.Column(
        db.String(30)
    )

    observaciones = db.Column(
        db.Text
    )

    activo = db.Column(
        db.Boolean,
        default=True
    )

    asistencias = db.relationship(
        "Asistencia",
        back_populates="servicio"
    )

    def __repr__(self):
        return f"<Servicio {self.clave} - {self.nombre}>"

# ==========================================================
# HORARIOS
# ==========================================================
class Horario(db.Model):
    __tablename__ = "horarios"

    id = db.Column(db.Integer, primary_key=True)

    clave = db.Column(
        db.String(20),
        unique=True,
        nullable=False
    )

    nombre = db.Column(
        db.String(80),
        nullable=False
    )

    hora_entrada = db.Column(
        db.Time,
        nullable=False
    )

    hora_salida = db.Column(
        db.Time,
        nullable=False
    )

    tolerancia = db.Column(
        db.Integer,
        default=10
    )

    observaciones = db.Column(
        db.Text
    )

    activo = db.Column(
        db.Boolean,
        default=True
    )
    asignaciones = db.relationship(
    "Asignacion",
    back_populates="horario"
    )

    asistencias = db.relationship(
    "Asistencia",
    back_populates="horario"
    )

    def __repr__(self):
        return f"<Horario {self.clave} - {self.nombre}>"
    
# ==========================================================
# ASIGNACIONES
# ==========================================================
class Asignacion(db.Model):
    __tablename__ = "asignaciones"

    id = db.Column(db.Integer, primary_key=True)

    empleado_id = db.Column(
        db.Integer,
        db.ForeignKey("empleados.id"),
        nullable=False
    )

    servicio_id = db.Column(
        db.Integer,
        db.ForeignKey("servicios.id"),
        nullable=False
    )

    horario_id = db.Column(
        db.Integer,
        db.ForeignKey("horarios.id"),
        nullable=False
    )

    fecha_inicio = db.Column(
        db.Date,
        nullable=False
    )

    fecha_fin = db.Column(
        db.Date
    )

    activo = db.Column(
        db.Boolean,
        default=True
    )

    empleado = db.relationship(
        "Empleado",
        backref="asignaciones"
    )

    servicio = db.relationship(
        "Servicio",
        backref="asignaciones"
    )

    horario = db.relationship(
    "Horario",
    back_populates="asignaciones"
    )
    
    def __repr__(self):
        return (
            f"<Asignacion "
            f"{self.empleado_id} -> {self.servicio_id}>"
        ) 
# ==========================================================
# ASISTENCIAS
# ==========================================================
class Asistencia(db.Model):
    __tablename__ = "asistencias"

    id = db.Column(db.Integer, primary_key=True)

    empleado_id = db.Column(
        db.Integer,
        db.ForeignKey("empleados.id"),
        nullable=False
    )

    servicio_id = db.Column(
        db.Integer,
        db.ForeignKey("servicios.id"),
        nullable=True
    )

    horario_id = db.Column(
        db.Integer,
        db.ForeignKey("horarios.id"),
        nullable=True
    )

    fecha_hora = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    tipo = db.Column(
        db.String(20),
        nullable=False
    )  # Entrada / Salida

    estatus = db.Column(
        db.String(20)
    )  # Puntual / Retardo / Salida

    latitud = db.Column(db.Float)

    longitud = db.Column(db.Float)

    precision = db.Column(db.Float)

    direccion = db.Column(
        db.String(250)
    )

    foto = db.Column(
        db.String(250)
    )

    ip = db.Column(
        db.String(50)
    )

    dispositivo = db.Column(
        db.String(150)
    )

    navegador = db.Column(
        db.String(150)
    )

    observaciones = db.Column(
        db.Text
    )

    empleado = db.relationship(
        "Empleado",
        back_populates="asistencias"
    )

    servicio = db.relationship(
        "Servicio",
        back_populates="asistencias"
    )

    horario = db.relationship(
        "Horario"
    )

    def __repr__(self):
        return (
            f"<Asistencia {self.id} - "
            f"{self.tipo} - "
            f"{self.estatus}>"
        )
# ==========================================================
# BITÁCORA DEL SISTEMA
# ==========================================================
class Bitacora(db.Model):
    __tablename__ = "bitacora"

    id = db.Column(db.Integer, primary_key=True)

    fecha = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    usuario = db.Column(db.String(100))

    accion = db.Column(db.String(100))

    descripcion = db.Column(db.Text)

    ip = db.Column(db.String(50))

    def __repr__(self):
        return f"<Bitacora {self.accion}>"
    