from datetime import datetime
from datetime import datetime, date

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

    # ======================================================
    # IDENTIFICACIÓN
    # ======================================================

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    numero_empleado = db.Column(
        db.String(20),
        unique=True,
        nullable=False
    )

    nombre = db.Column(
        db.String(80),
        nullable=False
    )

    apellido_paterno = db.Column(
        db.String(80),
        nullable=False
    )

    apellido_materno = db.Column(
        db.String(80)
    )
    horario_id = db.Column(
    db.Integer,
    db.ForeignKey("horarios.id"),
    nullable=True
    )

    horario = db.relationship(
    "Horario",
    back_populates="empleados"
)
    # ======================================================
    # INFORMACIÓN LABORAL
    # ======================================================

    puesto = db.Column(
        db.String(80),
        nullable=False
    )

    departamento = db.Column(
        db.String(100)
    )

    jefe_inmediato = db.Column(
        db.String(100)
    )

    fecha_ingreso = db.Column(
        db.Date
    )

    # ======================================================
    # HORARIO
    # ======================================================

    hora_entrada = db.Column(
        db.Time
    )

    hora_salida = db.Column(
        db.Time
    )

    turno = db.Column(
        db.String(30)
    )

    dias_descanso = db.Column(
        db.String(100)
    )

    # ======================================================
    # CONTACTO
    # ======================================================

    telefono = db.Column(
        db.String(20)
    )

    correo = db.Column(
        db.String(120)
    )

    # ======================================================
    # ESTADO
    # ======================================================

    estatus = db.Column(
        db.String(20),
        default="Activo"
    )

    activo = db.Column(
        db.Boolean,
        default=True
    )

    # ======================================================
    # RELACIONES
    # ======================================================

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

    actividades = db.relationship(
        "Actividad",
        back_populates="empleado",
        cascade="all, delete-orphan"
    )

    actividades_asignadas = db.relationship(
        "ActividadAsignada",
        back_populates="empleado",
        cascade="all, delete-orphan"
    )

    asignaciones = db.relationship(
        "Asignacion",
        back_populates="empleado",
        cascade="all, delete-orphan"
    )
    horario = db.relationship(
    "Horario",
    back_populates="empleados"
    )
    # ======================================================
    # MÉTODOS
    # ======================================================

    def nombre_completo(self):
        return (
            f"{self.nombre} "
            f"{self.apellido_paterno} "
            f"{self.apellido_materno or ''}"
        ).strip()

    def __repr__(self):
        return (
            f"<Empleado "
            f"{self.numero_empleado} - "
            f"{self.nombre_completo()}>"
        )
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

    asignaciones = db.relationship(
        "Asignacion",
        back_populates="servicio",
        cascade="all, delete-orphan"
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
    back_populates="horario",
    cascade="all, delete-orphan"
    )

    asistencias = db.relationship(
    "Asistencia",
    back_populates="horario"
    )

    empleados = db.relationship(
    "Empleado",
    back_populates="horario"
)

    def __repr__(self):
        return f"<Horario {self.clave} - {self.nombre}>"
    
# ==========================================================
# ASIGNACIONES
# ==========================================================
class Asignacion(db.Model):
    __tablename__ = "asignaciones"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

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

    # Se conserva temporalmente para no romper el sistema
    horario_id = db.Column(
        db.Integer,
        db.ForeignKey("horarios.id"),
        nullable=False
    )

    # Campos actuales (se conservan por compatibilidad)
    fecha_inicio = db.Column(
        db.Date,
        nullable=False
    )

    fecha_fin = db.Column(
        db.Date,
        nullable=True
    )

    # ========= NUEVOS CAMPOS =========

    fecha_programada = db.Column(
        db.Date,
        nullable=True
    )

    prioridad = db.Column(
        db.String(20),
        nullable=False,
        default="Media"
    )

    estado = db.Column(
        db.String(20),
        nullable=False,
        default="Pendiente"
    )

    observaciones = db.Column(
        db.Text,
        nullable=True
    )

    # ================================

    activo = db.Column(
        db.Boolean,
        default=True
    )

    empleado = db.relationship(
        "Empleado",
        back_populates="asignaciones"
    )

    servicio = db.relationship(
        "Servicio",
        back_populates="asignaciones"
    )

    horario = db.relationship(
        "Horario",
        back_populates="asignaciones"
    )

    def __repr__(self):
        return (
            f"<Asignacion "
            f"{self.empleado.nombre if self.empleado else ''} - "
            f"{self.servicio.nombre if self.servicio else ''} - "
            f"{self.estado}>"
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
        "Horario",
        back_populates="asistencias"    
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

class Actividad(db.Model):

    __tablename__ = "actividades"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    empleado_id = db.Column(
        db.Integer,
        db.ForeignKey("empleados.id"),
        nullable=False
    )

    fecha = db.Column(
        db.Date,
        nullable=False,
        default=date.today
    )

    actividad = db.Column(
        db.String(200),
        nullable=False
    )

    descripcion = db.Column(
        db.Text
    )

    hora_inicio = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.now
    )

    hora_fin = db.Column(
        db.DateTime
    )

    estado = db.Column(
        db.String(20),
        nullable=False,
        default="En proceso"
    )

    observaciones = db.Column(
        db.Text
    )

    empleado = db.relationship(
        "Empleado",
        back_populates="actividades"
    )

    @property
    def duracion(self):

        if self.hora_inicio and self.hora_fin:

            diferencia = self.hora_fin - self.hora_inicio

            total_segundos = int(diferencia.total_seconds())

            horas = total_segundos // 3600

            minutos = (total_segundos % 3600) // 60

            return f"{horas:02}:{minutos:02}"

        return ""

class ActividadAsignada(db.Model):
        __tablename__ = "actividades_asignadas"

        id = db.Column(db.Integer, primary_key=True)

        empleado_id = db.Column(
            db.Integer,
            db.ForeignKey("empleados.id"),
            nullable=False
        )

        actividad = db.Column(
            db.String(200),
            nullable=False
        )

        descripcion = db.Column(
            db.Text
        )

        fecha_programada = db.Column(
            db.Date,
            nullable=False
        )

        prioridad = db.Column(
            db.String(20),
            default="Media"
        )   

        estado = db.Column(
            db.String(20),
            default="Pendiente"
        )

        observaciones = db.Column(
            db.Text
        )

        fecha_creacion = db.Column(
            db.DateTime,
            default=datetime.now
        )

        empleado = db.relationship(
            "Empleado",
            back_populates="actividades_asignadas"
        )

        def __repr__(self):
            return f"<ActividadAsignada {self.actividad} - {self.estado}>"