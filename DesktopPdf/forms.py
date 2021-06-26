from flask_wtf import FlaskForm
from wtforms import TextField
from flask_wtf.file import FileField, FileRequired
from wtforms.validators import Required


class LogInForm(FlaskForm):
    password = TextField(u"Password", validators=[Required()])


class PhotoForm(FlaskForm):
    photo = FileField(validators=[FileRequired()])
