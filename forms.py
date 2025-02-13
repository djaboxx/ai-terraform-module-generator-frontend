from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, URL, Regexp

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Register')

class ProfileForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    current_password = PasswordField('Current Password')
    new_password = PasswordField('New Password', validators=[Length(min=6)])
    confirm_password = PasswordField('Confirm New Password', validators=[EqualTo('new_password')])
    role = SelectField('Role', choices=[('reader', 'Reader'), ('publisher', 'Publisher')], default='reader')
    submit = SubmitField('Update Profile')

class RepositoryForm(FlaskForm):
    repo_url = StringField('Repository URL', validators=[
        DataRequired(),
        URL(message="Please enter a valid URL"),
        Regexp(
            r'^https?://github\.com/[\w-]+/[\w-]+(?:\.git)?$',
            message="Please enter a valid GitHub repository URL"
        )
    ])

class AdminUserForm(FlaskForm):
    role = StringField('Role', validators=[DataRequired()])
    permissions = StringField('Permissions')  # Comma-separated list of permissions
    namespaces = StringField('Namespaces')   # Comma-separated list of namespaces
    submit = SubmitField('Update User')