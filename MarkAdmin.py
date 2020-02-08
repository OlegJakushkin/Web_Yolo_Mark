from PIL import Image
from flask import request, redirect, url_for
from flask_admin import Admin, expose, BaseView
from flask_admin.babel import lazy_gettext
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.sqla.filters import BaseSQLAFilter
from flask_login import current_user
from wtforms import PasswordField
from transliterate import translit
from MarkDatabase import *


class RoledView(ModelView):
    role = 'admin'

    def is_accessible(self):
        access = current_user.is_authenticated and current_user.has_roles([self.role])
        return access

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            if current_user.is_authenticated:
                return redirect('/')
            return redirect(url_for('login', next=request.url))


class BaseRoledView(BaseView):
    role = 'admin'

    def is_accessible(self):
        access = current_user.is_authenticated and current_user.has_roles([self.role])
        return access

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            if current_user.is_authenticated:
                return redirect('/')
            return redirect(url_for('login', next=request.url))


class AdminView(RoledView):
    role = 'admin'


class AddUserView(AdminView):
    can_view_details = True
    can_create = True
    can_edit = True
    can_delete = True
    form_extra_fields = {
        'password': PasswordField('Password')
    }


class FilterPhrase(BaseSQLAFilter):
    def apply(self, query, value, alias=None):
        stmt = "%{phrase}%".format(phrase=value)
        return query.filter(self.get_column(alias).ilike(stmt))

    def operation(self):
        return lazy_gettext('phrase')


class ObjectView(RoledView):
    role = 'marker'
    column_searchable_list = ['name', 'description']

    column_filters = (
        FilterPhrase(ObjectClass.name, "Название"),
        FilterPhrase(ObjectClass.description, "Описание"),
    )


class UploadImagesView(BaseRoledView):
    role = 'uploader'

    def __init__(self, photos, db, **kwargs):
        super(UploadImagesView, self).__init__(**kwargs)
        self.photos = photos
        self.db = db

    @expose('/', methods=('GET', 'POST'))
    def index(self):
        if request.method == 'POST':
            file_obj = request.files
            for f in file_obj:
                file = request.files.get(f)
                try:
                    file.filename = translit(file.filename , reversed=True,  fail_silently=True)
                except:
                    pass
                # save the file with to our photos folder
                filename = self.photos.save(file)
                im = Image.open(file.stream)
                w, h = im.size
                foto = File(image=filename, width=w, height=h)
                self.db.session.add(foto)
                self.db.session.commit()

            return "uploading..."
        return self.render('images_add_page.html')


def CreateWallAdmin(app, db):
    admin = Admin(app, name='Разметка изображений', template_mode='bootstrap3', url='/')
    admin.add_view(AddUserView(User, db.session, 'Пользователи'))
    admin.add_view(ObjectView(ObjectClass, db.session, 'Классы Объектов'))
    admin.add_view(AdminView(File, db.session, 'Картинки'))
    admin.add_view(UploadImagesView(app.photos, db, name='Загрузка Изображений'))
    return admin
