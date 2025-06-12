#aqui importamos flask
from flask import Flask, render_template, redirect, url_for, flash
#paso 1 aqui importamos sqlalchemy para el manejo de mi Base de datos(ORM)
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

#imagenes
import os
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename

#login
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

app = Flask(__name__)
#la clave secreta
app.config['SECRET_KEY'] = 'tu_clave_secreta' 


UPLOAD_FOLDER = 'static/imagenes'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'tu_clave_secreta'  # Necesaria para Flash Messages

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#fin imagenes


#aqui importamos wtf form
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length, Optional

from wtforms import DateField

from wtforms import FileField
from flask_wtf.file import FileField

from wtforms.validators import Optional

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length

#paso 2 Aqui configuramos la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///peliculas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] =  False

#configuramos login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "logeo"  # Redirige a la página de login si el usuario no está autenticado


#paso 3 definimos la variable
db = SQLAlchemy(app)

#paso 4 definimos las clases (estas seran nuestras tablas)

#definimos la clase categorias

class Categoria(db.Model):
    __tablename__ = 'categorias'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    descripcion = db.Column(db.String(255), nullable=False)


#definimos la clase administradores con el login

class Administrador(UserMixin, db.Model):
    __tablename__ = 'administradores'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usuario = db.Column(db.String(255), unique=True, nullable=False)
    contraseña = db.Column(db.String(255), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return Administrador.query.get(int(user_id))

@app.route('/logeo', methods=['GET', 'POST'])
def logeo():
    if request.method == 'POST':
        usuario = request.form['username']
        contraseña = request.form['password']
        
        admin = Administrador.query.filter_by(usuario=usuario).first()

        if admin and admin.contraseña == contraseña:  # Usa hashing en producción
            login_user(admin)
            flash("¡Bienvenido, administrador!", "success")
            return redirect(url_for("crud"))
        else:
            flash("Credenciales incorrectas.", "danger")

    return render_template('login.html')

#fin de definimos la clase administradores con el login

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)


#definimos la clase noticias
class Noticia(db.Model):
    __tablename__ = 'noticias'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    titulo = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.String(500), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    imagen = db.Column(db.String(255), nullable=True)  # Para manejar imágenes opcionales

#definimos la clase jornadas
class JornadaMedica(db.Model):
    __tablename__ = 'jornadas_medicas'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    titulo = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.String(500), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    hora = db.Column(db.String(10), nullable=False)  # Nuevo campo
    lugar = db.Column(db.String(255), nullable=False)  # Nuevo campo
    imagen = db.Column(db.String(255), nullable=True)  # Imagen opcional

#paso 5 creando todas las tablas partiendo de Modelos declarados
with app.app_context():
    print("Creando tablas...")
    db.create_all()
    print("Hemos logrado el objetivo muchachos yeiiii")

#aqui vamos a declarar las clases para nuestros formularios
#clase peliculas
class NoticiaForm(FlaskForm):
    titulo = StringField('Título', validators=[DataRequired(), Length(max=255)])
    descripcion = StringField('Descripción', validators=[DataRequired(), Length(max=500)])
    fecha = StringField('Fecha', validators=[DataRequired(), Length(max=10)])  # Usa formato YYYY-MM-DD
    submit = SubmitField('Enviar')



# AHORA CREAMOS UNA PARA LOS USUARIOS Y ADMINISTRADORES

class AdministradorForm(FlaskForm):
    usuario = StringField('Usuario', validators=[DataRequired(), Length(max=255)])
    contraseña = StringField('Contraseña', validators=[DataRequired(), Length(max=255)])
    submit = SubmitField('Registrar')

@app.route('/registrar_administrador', methods=['GET', 'POST'])
def registrar_administrador():
    form = AdministradorForm()
    if form.validate_on_submit():
        nuevo_admin = Administrador(
            usuario=form.usuario.data,
            contraseña=form.contraseña.data
        )
        db.session.add(nuevo_admin)
        db.session.commit()
        flash('Administrador registrado exitosamente!', 'success')
        return redirect(url_for('registrar_administrador'))
    return render_template('administrador/registro_administrador.html', form=form)

class UsuarioForm(FlaskForm):
    username = StringField('Nombre de usuario', validators=[DataRequired(), Length(max=100)])
    email = StringField('Correo electrónico', validators=[DataRequired(), Length(max=100)])  # Cambiado de EmailField a StringField
    password = StringField('Contraseña', validators=[DataRequired(), Length(max=100)])  # Cambiado de PasswordField a StringField
    submit = SubmitField('Registrar')


@app.route('/registrar_usuario', methods=['GET', 'POST'])
def registrar_usuario():
    form = UsuarioForm()
    if form.validate_on_submit():
        nuevo_usuario = Usuario(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data
        )
        db.session.add(nuevo_usuario)
        db.session.commit()
        flash('Usuario registrado exitosamente!', 'success')
        return redirect(url_for('registrar_usuario'))
    
    return render_template('registro_usuario.html', form=form)  # 👈 Aquí pasamos form correctamente


# FIN DE RUTA Admin
#ruta jornada

class JornadaMedicaForm(FlaskForm):
    titulo = StringField('Título', validators=[DataRequired(), Length(max=255)])
    descripcion = StringField('Descripción', validators=[DataRequired(), Length(max=500)])
    fecha = DateField('Fecha', format='%Y-%m-%d', validators=[DataRequired()])
    hora = StringField('Hora', validators=[DataRequired(), Length(max=10)])  # Nuevo campo
    lugar = StringField('Lugar', validators=[DataRequired(), Length(max=255)])  # Nuevo campo
    imagen = FileField('Imagen', validators=[Optional()])
    submit = SubmitField('Registrar')

@app.route('/agregar_jornada', methods=['GET', 'POST'])
def agregar_jornada():
    form = JornadaMedicaForm()
    if form.validate_on_submit():
        titulo = form.titulo.data
        descripcion = form.descripcion.data
        fecha = form.fecha.data
        hora = form.hora.data  # Nuevo campo
        lugar = form.lugar.data  # Nuevo campo

        archivo = request.files.get('imagen')
        nombre_imagen = None

        if archivo and allowed_file(archivo.filename):
            nombre_imagen = secure_filename(archivo.filename)
            archivo.save(os.path.join(app.config['UPLOAD_FOLDER'], nombre_imagen))

        nueva_jornada = JornadaMedica(
            titulo=titulo,
            descripcion=descripcion,
            fecha=fecha,
            hora=hora,  # Guardar en la base de datos
            lugar=lugar,  # Guardar en la base de datos
            imagen=nombre_imagen
        )
        db.session.add(nueva_jornada)
        db.session.commit()
        flash('¡Jornada médica agregada exitosamente!', 'success')
        return redirect(url_for('agregar_jornada'))

    return render_template('administrador/agregar_jornada.html', form=form)

@app.route('/editar_jornada/<int:id>', methods=['GET', 'POST'])
def editar_jornada(id):
    jornada = JornadaMedica.query.get_or_404(id)
    form = JornadaMedicaForm(obj=jornada)

    if form.validate_on_submit():
        jornada.titulo = form.titulo.data
        jornada.descripcion = form.descripcion.data
        jornada.fecha = form.fecha.data
        jornada.hora = form.hora.data  # Nuevo campo
        jornada.lugar = form.lugar.data  # Nuevo campo

        # Manejo de actualización de imagen
        archivo = request.files.get('imagen')
        if archivo and allowed_file(archivo.filename):
            nombre_imagen = secure_filename(archivo.filename)
            archivo.save(os.path.join(app.config['UPLOAD_FOLDER'], nombre_imagen))
            jornada.imagen = nombre_imagen  # Actualizar imagen solo si se sube nueva

        db.session.commit()
        flash('¡Jornada médica actualizada exitosamente!', 'success')
        return redirect(url_for('vista_jornadas'))

    return render_template('administrador/editar_jornadas.html', form=form, jornada=jornada)

@app.route('/eliminar_jornada/<int:id>', methods=['POST'])
def eliminar_jornada(id):
    jornada = JornadaMedica.query.get_or_404(id)
    db.session.delete(jornada)
    db.session.commit()
    flash('¡Jornada médica eliminada exitosamente!', 'success')
    return redirect(url_for('vista_jornadas'))


#ruta imagenes

@app.route('/agregar_noticia', methods=['GET', 'POST'])
def agregar_noticia():
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        descripcion = request.form.get('descripcion')
        fecha_str = request.form.get('fecha')  # La fecha viene como string

        # Convertimos la fecha a un objeto date de Python
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()

        archivo = request.files.get('imagen')
        nombre_imagen = None

        if archivo and allowed_file(archivo.filename):
            nombre_imagen = secure_filename(archivo.filename)
            archivo.save(os.path.join(app.config['UPLOAD_FOLDER'], nombre_imagen))

        nueva_noticia = Noticia(
            titulo=titulo,
            descripcion=descripcion,
            fecha=fecha,  # Ahora `fecha` es un objeto date válido
            imagen=nombre_imagen
        )
        db.session.add(nueva_noticia)
        db.session.commit()
        flash('¡Noticia agregada exitosamente!', 'success')
        return redirect(url_for('agregar_noticia'))

    return render_template('administrador/agregar_noticia.html')

#fin ruta imagenes

#modificar y eliminar peliculas

@app.route('/editar_noticia/<int:id>', methods=['GET', 'POST'])
def editar_noticia(id):
    noticia = Noticia.query.get_or_404(id)
    form = NoticiaForm(obj=noticia)

    if form.validate_on_submit():
        noticia.titulo = form.titulo.data
        noticia.descripcion = form.descripcion.data
        
        # Convertimos la fecha de string a date
        fecha_str = form.fecha.data
        if isinstance(fecha_str, str):  # Solo convertir si es cadena
            noticia.fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        else:
            noticia.fecha = fecha_str  # Mantener si ya es objeto date
        
        db.session.commit()
        flash('¡Noticia actualizada exitosamente!', 'success')
        return redirect(url_for('principal'))

    return render_template('administrador/editar_noticia.html', form=form, noticia=noticia)


@app.route('/eliminar_noticia/<int:id>', methods=['POST'])
def eliminar_noticia(id):
    noticia = Noticia.query.get_or_404(id)
    db.session.delete(noticia)
    db.session.commit()
    flash('¡Noticia eliminada exitosamente!', 'success')
    return redirect(url_for('principal'))
#fin modificar y eliminar peliculas

@app.route('/')
def principal():
    # Recuperar todas las noticias desde la tabla
    noticias = Noticia.query.all()
    return render_template('usuario/principal.html', noticias=noticias)

@app.route('/vista_publica')
def vista_publica():
    noticias = Noticia.query.all()
    return render_template('vista_publica.html', noticias=noticias)

@app.route('/crud')
@login_required
def crud():
    return render_template("administrador/CRUD.html", usuario=current_user.usuario)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada correctamente.", "success")
    return redirect(url_for("logeo"))

@app.route('/inicio')
def inicio():
    return render_template('usuario/inicio.html',)

@app.route('/quienes')
def quienes():
    return render_template('usuario/quienes.html',)

@app.route('/contacto')
def contacto():
    return render_template('usuario/contacto.html',)

@app.route('/servicio')
def servicio():
    return render_template('usuario/servicio.html',)

@app.route('/editar_jornadas')
def vista_jornadas():
    jornadas = JornadaMedica.query.all()
    return render_template('usuario/vista_jornada.html', jornadas=jornadas)

@app.route('/vista_jornadas')
def jornadas():
    jornadas = JornadaMedica.query.all()
    return render_template('usuario/jornada_publico.html', jornadas=jornadas)

if __name__ == '__main__':
    app.run(debug=True)