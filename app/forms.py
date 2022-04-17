from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length, EqualTo

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(message="Please enter your email"), Email(message="Please enter a valid email")], render_kw={'autofocus': True})
    password = PasswordField('Password', validators=[InputRequired(message="Password required")])
    remember_me = BooleanField('Remember me')
    submit_button = SubmitField('Login')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField("Enter your email", validators=[InputRequired(message="Please enter your email"), Email(message="Please enter a valid email")], render_kw={'autofocus': True})
    submit_button = SubmitField("Request Password Reset")

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New password',
        validators=[InputRequired(message="Password required"), 
        Length(min=8, message="Password must be at least 8 characters")], 
        render_kw={'autofocus': True})
    confirm_pswd = PasswordField('Confirm new password',
        validators=[InputRequired(message="Password required"), 
        EqualTo("password", message="Passwords must match")])
    submit_button = SubmitField("Submit new password")
