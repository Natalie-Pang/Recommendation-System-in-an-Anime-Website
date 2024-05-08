from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
import re
from flask_wtf.file import FileField, FileAllowed
from werkzeug.utils import secure_filename

def symbol_check(form, field):
    excluded_char = "*?!'^+%&/()=}][{$#@<>"
    for char in field.data:
        if char in excluded_char:
            raise ValidationError(f"Character {char} is not allowed")

# regex to check whether the field contains at least one uppercase character, lowercase character, digit and special character
def all_check(form, data_field):
    p = re.compile("^(?=.*[a-z])(?=.*[A-Z])(?=.*[@#$%^&+=])(?=.*[0-9]).*$")
    if not p.match(data_field.data):
        raise ValidationError("Must contain at least one uppercase character, lowercase character, digit and special character")

class RegisterForm(FlaskForm):
    username = StringField(validators=[DataRequired(message='Data required'), Length(min=6, max=15), symbol_check])
    email = StringField(validators=[DataRequired(), Email()])
    password1 = PasswordField(validators=[DataRequired(), Length(min=6, max=12), all_check])
    password2 = PasswordField(validators=[DataRequired(), EqualTo('password1', 'both password fields must be equal')])
    submit = SubmitField()

class LoginForm(FlaskForm):
    email = StringField(validators=[DataRequired(), Email()])
    password = PasswordField(validators=[DataRequired()])
    submit = SubmitField()

class ProfilePictureForm(FlaskForm):
    profile_picture = FileField('Profile Picture', validators=[DataRequired(), FileAllowed(['jpg', 'png'], 'Images only!')])

class UpdateInfoForm(FlaskForm):
    username = StringField(validators=[DataRequired(message='Data required'), Length(min=6, max=15), symbol_check])
    email = StringField(validators=[DataRequired(), Email()])
    submit = SubmitField()

class CreateDiscussionForm(FlaskForm):
    title = StringField('Discussion Title', validators=[DataRequired()])
    content = StringField('Message Content', validators=[DataRequired()])
    submit = SubmitField('Create Discussion')