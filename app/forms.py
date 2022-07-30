from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, SubmitField, BooleanField
from wtforms.validators import Length, EqualTo, DataRequired, ValidationError

from .models import UserModel


class RegisterForm(FlaskForm):
    """Form for registration"""

    def validate_username(self, username_to_check):
        username = UserModel.find_by_username(username=username_to_check.data)
        if username:
            raise ValidationError('Username already exists! Please, try a different username')

    def validate_email(self, user_email_to_check):
        email = UserModel.find_by_email(email=user_email_to_check.data)
        if email:
            raise ValidationError('Such email already exists! Please, try a different one!')

    name = StringField(label='Your Name:', validators=[Length(min=1, max=60), DataRequired()])
    age = IntegerField(label='Age:', validators=[DataRequired()])
    username = StringField(label='Username:', validators=[Length(min=3, max=60), DataRequired()])
    email = StringField(label='Email Address:', validators=[DataRequired()])
    password1 = PasswordField(label='Password:', validators=[Length(min=2, max=60), DataRequired()])
    password2 = PasswordField(label='Confirm Password:', validators=[EqualTo('password1')])
    checkbox = BooleanField(label='Is Admin:', default=False)
    submit = SubmitField(label='Create Account')


class LoginForm(FlaskForm):
    """Form to log in"""
    username = StringField(label='User Name:', validators=[DataRequired()])
    password = StringField(label='Password:', validators=[DataRequired()])
    submit = SubmitField(label='Sign in')


class SeatForm(FlaskForm):
    """Form to reserve a seat"""
    seat = IntegerField(label='Your seat:', validators=[DataRequired()])
    submit = SubmitField(label='Buy')
