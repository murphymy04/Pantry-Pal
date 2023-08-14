from flask_wtf import FlaskForm
from wtforms import SubmitField, PasswordField, EmailField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    email = EmailField('', validators=[DataRequired()], render_kw={"placeholder": "Email"})
    password = PasswordField('', render_kw={'placeholder': 'Password'}, validators=[DataRequired()])
    submit = SubmitField("Login")