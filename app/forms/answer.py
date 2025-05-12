from flask_wtf import FlaskForm
from wtforms import TextAreaField, FileField, SubmitField
from wtforms.validators import DataRequired, Length

class AnswerForm(FlaskForm):
    """Form for submitting answers to questions."""
    body = TextAreaField('Your Answer', validators=[
        DataRequired(),
        Length(min=20, message='Your answer must be at least 20 characters long.')
    ])
    attachments = FileField('Attachments (Optional)')
    submit = SubmitField('Post Your Answer')

class CommentForm(FlaskForm):
    """Form for adding comments to questions or answers."""
    body = TextAreaField('Your Comment', validators=[
        DataRequired(),
        Length(min=5, max=500, message='Comments must be between 5 and 500 characters.')
    ])
    submit = SubmitField('Add Comment')

