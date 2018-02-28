# coding=utf-8

# Sin el coding me saltaba un error...
import os
import os.path as op

from flask import Flask, url_for
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy.event import listens_for
from jinja2 import Markup

from flask_admin import Admin, form
from flask_admin.form import rules
from flask_admin.contrib import sqla


# Create app
app = Flask(__name__, static_folder='files')

# Clave secreta ficticia para que se puedan usar sesiones..
app.config['SECRET_KEY'] = '123456790'

# Create in-memory database (sqlite)
app.config['DATABASE_FILE'] = 'sample_db.sqlite'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + app.config['DATABASE_FILE']
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

# Create directory for file fields to use
file_path = op.join(op.dirname(__file__), 'files')
try:
    os.mkdir(file_path)
except OSError:
    pass


# Create models
class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(64))
    path = db.Column(db.Unicode(128))

    def __unicode__(self):
        return self.name


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(64))
    path = db.Column(db.Unicode(128))

    def __unicode__(self):
        return self.name


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.Unicode(64))
    last_name = db.Column(db.Unicode(64))
    email = db.Column(db.Unicode(128))
    phone = db.Column(db.Unicode(32))
    city = db.Column(db.Unicode(128))
    country = db.Column(db.Unicode(128))
    notes = db.Column(db.UnicodeText)


@listens_for(File, 'after_delete')
def del_file(mapper, connection, target):
    if target.path:
        try:
            os.remove(op.join(file_path, target.path))
        except OSError:
            # Error que salta cuando se elimina algo que no existe
            pass


@listens_for(Image, 'after_delete')
def del_image(mapper, connection, target):
    if target.path:
        # Eliminar imagenes
        try:
            os.remove(op.join(file_path, target.path))
        except OSError:
            pass

        # Eliminar miniaturas
        try:
            os.remove(op.join(file_path,
                              form.thumbgen_filename(target.path)))
        except OSError:
            pass


# Administración de las vistas
class FileView(sqla.ModelView):
    # Anular campo de formulario para usar Flask-Admin FileUploadField
    form_overrides = {
        'path': form.FileUploadField
    }

    # Pasar parámetros adicionales a 'ruta' al constructor FileUploadField
    form_args = {
        'path': {
            'label': 'File',
            'base_path': file_path,
            'allow_overwrite': False
        }
    }


class ImageView(sqla.ModelView):
    def _list_thumbnail(view, context, model, name):
        if not model.path:
            return ''

        return Markup('<img src="%s">' % url_for('static',
                                                 filename=form.thumbgen_filename(model.path)))

    column_formatters = {
        'path': _list_thumbnail
    }

    # En este caso, Flask-Admin no intentará fusionar varios parámetros para el campo.
    form_extra_fields = {
        'path': form.ImageUploadField('Image',
                                      base_path=file_path,
                                      thumbnail_size=(100, 100, True))
    }


class UserView(sqla.ModelView):
    """
    Esta clase demuestra el uso de 'reglas' para controlar la representación de formularios.
    """
    form_create_rules = [
        # Header y los 4 campos..
        rules.FieldSet(('first_name', 'last_name', 'email', 'phone'), 'Personal'),
        # Separando headr y campos
        rules.Header('Location'),
        rules.Field('city'),
        'country',
        # Mostrar macro de Flask-Admin lib.html (se incluye con el prefijo 'lib')
        rules.Container('rule_demo.wrap', rules.Field('notes'))
    ]

    # Use same rule set for edit page
    form_edit_rules = form_create_rules

    create_template = 'rule_create.html'
    edit_template = 'rule_edit.html'


# Flask views
@app.route('/')
def index():
    return '<a href="/admin/">Clic para entrar en administración</a>'

# Aquí se crea el administrador
admin = Admin(app, 'Ejemplo: formularios', template_mode='bootstrap3')

# Se añaden las vistas
admin.add_view(FileView(File, db.session, name='Ficheros'))
admin.add_view(ImageView(Image, db.session, name='Imagenes'))
admin.add_view(UserView(User, db.session, name='Usuarios'))


def build_sample_db():
    """
    Se introducirán algunos datos de ejemplo en la bd
    """

    import random
    import string

    db.drop_all()
    db.create_all()

    first_names = [
        'Juan', 'Pepe', 'Paulino', 'Javier', 'Cristian', 'Fran','Sofia', 'Marina',
        'Pepito', 'Popo', 'Paulo', 'Pinpon', 'Evaristo', 'Isla', 'Alfie', 'Olivia', 'Jessica',
        'Riley', 'William', 'James', 'Jeffry', 'Jessica', 'Fredy', 'Amanda', 'Lucy'
    ]
    last_names = [
        'Delgado', 'DeJuan', 'Huertas', 'Jimenez', 'DelosSantos', 'Alcon', 'Taylor', 'Thomas',
        'Roberts', 'Khan', 'Lewis', 'Jackson', 'Clarke', 'James', 'Phillips', 'Wilson',
        'Ali', 'Mason', 'Mitchell', 'Rose', 'Davis', 'Davies', 'Jerbi', 'Cox', 'Alexander'
    ]
    locations = [
        ("Shanghai", "China"),
        ("Istanbul", "Turkey"),
        ("Karachi", "Pakistan"),
        ("Mumbai", "India"),
        ("Moscow", "Russia"),
        ("Sao Paulo", "Brazil"),
        ("Beijing", "China"),
        ("Tianjin", "China"),
        ("Guangzhou", "China"),
        ("Delhi", "India"),
        ("Seoul", "South Korea"),
        ("Shenzhen", "China"),
        ("Jakarta", "Indonesia"),
        ("Tokyo", "Japan"),
        ("Mexico City", "Mexico"),
        ("Kinshasa", "Democratic Republic of the Congo"),
        ("Bangalore", "India"),
        ("New York City", "United States"),
        ("London", "United Kingdom"),
        ("Bangkok", "Thailand"),
        ("Tehran", "Iran"),
        ("Dongguan", "China"),
        ("Lagos", "Nigeria"),
        ("Lima", "Peru"),
        ("Ho Chi Minh City", "Vietnam"),
        ]

    for i in range(len(first_names)):
        user = User()
        user.first_name = first_names[i]
        user.last_name = last_names[i]
        user.email = user.first_name.lower() + "@gmail.com"
        tmp = ''.join(random.choice(string.digits) for i in range(10))
        user.phone = "(" + tmp[0:3] + ") " + tmp[3:6] + " " + tmp[6::]
        user.city = locations[i][0]
        user.country = locations[i][1]
        db.session.add(user)

    # De aquí se cogen las imágenes y files
    images = ["Buffalo", "Elephant", "Leopard", "Lion", "Rhino"]
    for name in images:
        image = Image()
        image.name = name
        image.path = name.lower() + ".jpg"
        db.session.add(image)

    for i in [1, 2, 3]:
        file = File()
        file.name = "Example " + str(i)
        file.path = "example_" + str(i) + ".pdf"
        db.session.add(file)

    db.session.commit()
    return

if __name__ == '__main__':

    # Se realiza la build de la bd si no existe ya una
    app_dir = op.realpath(os.path.dirname(__file__))
    database_path = op.join(app_dir, app.config['DATABASE_FILE'])
    if not os.path.exists(database_path):
        build_sample_db()

    # Se lanza la app
    app.run(debug=True)
