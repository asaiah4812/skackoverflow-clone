from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, PasswordField, SubmitField, BooleanField, URLField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional
from flask_login import current_user
from app.models.user import User

class UpdateProfileForm(FlaskForm):
    """Form for updating user profile."""
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=20, message='Username must be between 3 and 20 characters.')
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email(message='Please enter a valid email address.')
    ])
    bio = TextAreaField('Bio', validators=[
        Optional(),
        Length(max=500, message='Bio cannot exceed 500 characters.')
    ])
    location = StringField('Location', validators=[
        Optional(),
        Length(max=100, message='Location cannot exceed 100 characters.')
    ])
    website = URLField('Website', validators=[
        Optional()
    ])
    profile_image = FileField('Profile Image', validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')
    ])
    submit = SubmitField('Update Profile')
    
    def validate_username(self, username):
        """Validate username is unique."""
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is already taken. Please choose a different one.')
    
    def validate_email(self, email):
        """Validate email is unique."""
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is already registered. Please choose a different one.')


