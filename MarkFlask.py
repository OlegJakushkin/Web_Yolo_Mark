import json

from flask import Flask, request, redirect, render_template, flash, url_for
from flask.templating import DispatchingJinjaLoader
from flask_babelex import Babel
from flask_caching import Cache
from flask_compress import Compress
# from flask_cors import CORS
from flask_dropzone import Dropzone
from flask_login import login_required, logout_user, current_user, LoginManager, login_user
from flask_restful import reqparse, Api, Resource
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from flask_wtf import FlaskForm
from sqlalchemy import func, or_
from sqlalchemy.orm.exc import MultipleResultsFound
from sqlalchemy.orm.exc import NoResultFound
from wtforms import StringField, PasswordField, SubmitField

from MarkDatabase import *


class LoginForm(FlaskForm):
    username = StringField('Username')
    password = PasswordField('Password')
    submit = SubmitField('Submit')


class WallFileLoader(DispatchingJinjaLoader):
    def __init__(self, app):
        super(WallFileLoader, self).__init__(app)

    def get_source(self, environment, template):
        contents, filename, uptodate = super(WallFileLoader, self).get_source(environment, template)
        if template == 'base.html':
            contents = contents.replace(u'MyApp', u'Разметка Изображений')
            contents = contents.replace(u'2014', u'2020')
            contents = contents.replace(u'MyCorp', u'')
        return contents, filename, uptodate


class WallApp(Flask):
    def __init__(self, **kwargs):
        super(WallApp, self).__init__('Wall', **kwargs)

    def create_global_jinja_loader(self):
        return WallFileLoader(self)


class ConfigClass(object):
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'T#IS IS @N 666 sECRET')
    dbpath = os.getenv('DB_PATH', "db/")
    dbpath += 'db.sqlite'

    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///'+dbpath)

    CSRF_ENABLED = True
    USER_APP_NAME = "Wall"
    USER_ENABLE_FORGOT_PASSWORD = False
    USER_ENABLE_REGISTER = False
    USER_ENABLE_EMAIL = False
    USER_ALLOW_LOGIN_WITHOUT_CONFIRMED_EMAIL = True
    USER_EMAIL_SENDER_NAME = 'Yolo'
    USER_EMAIL_SENDER_EMAIL = 'info@example.com'

    DROPZONE_UPLOAD_MULTIPLE = True
    DROPZONE_ALLOWED_FILE_CUSTOM = True
    DROPZONE_ALLOWED_FILE_TYPE = 'image/*'
    DROPZONE_REDIRECT_VIEW = 'results'

    imgpath = os.getenv('IMG_PATH', os.getcwd() + '/uploads')
    UPLOADED_PHOTOS_DEST = imgpath

    TEMPLATES_AUTO_RELOAD = True
    DROPZONE_MAX_FILE_SIZE = 20
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT: 6000

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    COMPRESS_MIMETYPES = ['svg', 'xml', 'font', 'script', 'stylesheet', 'png', 'svg+xml', 'document',
                          'xhr', 'html', 'js', 'css']

    USER_LOGIN_TEMPLATE = 'login.html'
    USER_REGISTER_TEMPLATE = 'login.html'


def CreateWallApp():
    app = WallApp(static_folder='assets', static_url_path='/assets')
    app.config.from_object(__name__ + '.ConfigClass')

    try:
        app.config.from_object('local_settings')
    except:
        pass

    # Use for Frontend debug
    # CORS(app, resources={r"/api/*": {"origins": "*"}})

    Compress(app)
    Cache(app)
    babel = Babel(app)
    login = LoginManager(app)

    def redirect_dest(fallback):
        dest = request.args.get('next')
        try:
            dest_url = url_for(dest)
        except:
            return redirect(fallback)
        return redirect(dest_url)

    @login.unauthorized_handler
    def handle_needs_login():
        flash("You have to be logged in to access this page.")
        return redirect(url_for('login', next=request.endpoint))

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']

            user = User.query.filter(or_(User.username == username, User.email == username)).first()
            if user is None or not user.check_password(password):
                flash("Sorry, but you could not log in.")
                redirect(url_for('home_page'))
            else:
                next = request.form['next']
                login_user(user, remember=True)
                return redirect(next)
        else:
            next = request.args.get('next')
            return render_template("login.html", next=next)

    login.login_view = 'login'

    @babel.localeselector
    def get_locale():
        return 'ru'

    app.dropzone = Dropzone(app)
    app.photos = UploadSet('photos', IMAGES)
    configure_uploads(app, app.photos)
    patch_request_class(app)  # set maximum file size, default is 16MB

    @app.template_filter('data_fmt')
    def data_fmt(filename):
        datatypes = {'image': 'gif,ico,jpe,jpeg,jpg,png,svg,webp'}

        t = 'unknown'
        for type, exts in datatypes.items():
            if filename.split('.')[-1] in exts:
                t = type
        return t

    @app.template_filter('icon_fmt')
    def icon_fmt(filename):
        icontypes = {'fa-picture-o': 'gif,ico,jpe,jpeg,jpg,png,svg,webp'}

        i = 'fa-file-o'
        for icon, exts in icontypes.items():
            if filename.split('.')[-1] in exts:
                i = icon
        return i

    @app.route('/')
    def home_page():
        users = db.session.query(func.count(User.id)).scalar()
        files = db.session.query(func.count(File.id)).scalar()
        classes = db.session.query(func.count(ObjectClass.id)).scalar()
        marked = db.session.query(File).filter(File.processed == True).count()
        is_logedin = current_user.is_authenticated
        return render_template("index.html", marked=str(marked), classes=str(classes), files=str(files),
                               users=str(users), is_logedin=is_logedin)

    @app.route('/images_page')
    @login_required
    def images_page():
        return render_template('images_page.html')

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('home_page'))

    api = Api(app)

    class Files(Resource):
        def get(self, page):
            pglen = 10
            record_query = File.query \
                .filter(File.updated_at <= lessthenNow()) \
                .paginate(int(page), pglen, False)

            files = record_query.items
            contents = []
            total = {'files': len(files), 'pglen': pglen}
            for file in files:
                filepath = app.photos.url(file.image)
                info = {}
                info['name'] = file.image
                info['width'] = file.width
                info['height'] = file.height
                info['pcsd'] = file.processed
                info['url'] = filepath
                info['type'] = 'file'

                contents.append(info)
            return {'contents': contents, 'total': total}

    class ObjectClasses(Resource):
        def get(self):
            contents = []

            items = ObjectClass.query.all()
            for tag in items:
                info = {}
                info['value'] = tag.name
                info['color'] = "rgb(" + str(tag.r) + ", " + str(tag.g) + ", " + str(tag.b) + ")"
                contents.append(info)

            return {'tags': contents}

    class ImageDescriptor(Resource):

        def __init__(self, session, **kwargs):
            super(Resource, self).__init__(**kwargs)
            self.session = session
            self.parser = reqparse.RequestParser()
            self.parser.add_argument('description')

        def get(self, name):
            try:
                file = self.session.query(File) \
                    .filter(File.image == name).one()
                return json.dumps({'status': 'ok', 'url': app.photos.url(file.image), 'description': file.description})
            except MultipleResultsFound:
                return json.dumps({'status': 'error', 'error': 'multiple files'})
            except NoResultFound:
                return json.dumps({'status': 'error', 'error': 'no such file'})

        def post(self, name):
            try:
                file = self.session.query(File) \
                    .filter(File.image == name).one()

                args = self.parser.parse_args()
                descr = args['description']
                if not descr:
                    return

                file.description = descr
                file.processed = True
                self.session.commit()

                return json.dumps({'status': 'ok'})
            except MultipleResultsFound:
                return json.dumps({'status': 'error', 'error': 'multiple files'})
            except NoResultFound:
                return json.dumps({'status': 'error', 'error': 'no such file'})

    api.add_resource(Files, '/api/v1/FilesREST/<page>')
    api.add_resource(ImageDescriptor, '/api/v1/ImageREST/<name>', resource_class_kwargs={'session': db.session})
    api.add_resource(ObjectClasses, '/api/v1/ObjectClassesREST')

    return app
