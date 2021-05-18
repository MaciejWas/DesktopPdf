from flask_wtf import FlaskForm
from wtforms import TextField, TextAreaField, DateTimeField, PasswordField
from flask_wtf.file import FileField, FileRequired
from wtforms.validators import Required
from werkzeug.utils import secure_filename


class NewPassForm(FlaskForm):
    password = TextField(u"New password", validators=[Required()])


class LogInForm(FlaskForm):
    password = TextField(u"Password", validators=[Required()])


class PhotoForm(FlaskForm):
    photo = FileField(validators=[FileRequired()])
