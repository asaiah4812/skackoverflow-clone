from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

class ChatForm(FlaskForm):
    """Form for chatbot interactions."""
    message = TextAreaField('Your Question', validators=[
        DataRequired(),
        Length(min=2, max=500, message='Message must be between 2 and 500 characters.')
    ])
    submit = SubmitField('Send')