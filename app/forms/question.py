from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectMultipleField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Optional

class QuestionForm(FlaskForm):
    """Form for creating and editing questions."""
    title = StringField('Title', validators=[
        DataRequired(),
        Length(min=15, max=150, message='Title must be between 15 and 150 characters.')
    ])
    body = TextAreaField('Body', validators=[
        DataRequired(),
        Length(min=30, message='Question body must be at least 30 characters.')
    ])
    tags = SelectMultipleField('Tags', coerce=int, validators=[
        DataRequired(message='Please select at least one tag.')
    ])
    attachments = FileField('Attachments (Optional)', validators=[
        FileAllowed(['jpg', 'png', 'jpeg', 'gif', 'pdf'], 'Only images and PDFs are allowed!')
    ])
    submit = SubmitField('Post Question')

class TagForm(FlaskForm):
    """Form for creating tags."""
    name = StringField('Tag Name', validators=[
        DataRequired(),
        Length(min=2, max=25, message='Tag name must be between 2 and 25 characters.')
    ])
    description = TextAreaField('Description', validators=[
        Length(max=200, message='Description cannot exceed 200 characters.')
    ])
    submit = SubmitField('Create Tag')

class SearchForm(FlaskForm):
    """Form for searching questions."""
    query = StringField('Search', validators=[Optional()])
    submit = SubmitField('Search')

class QuestionFilterForm(FlaskForm):
    """Form for filtering questions."""
    tags = SelectMultipleField('Filter by Tags', coerce=int)
    sort_by = SelectField('Sort By', choices=[
        ('recent', 'Most Recent'),
        ('popular', 'Most Popular'),
        ('unanswered', 'Unanswered'),
        ('most_answers', 'Most Answers')
    ])
    submit = SubmitField('Apply Filters')

