from datetime import datetime
from app import db
import re

class Tag(db.Model):
    """Tag model for categorizing questions."""
    __tablename__ = 'tags'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    slug = db.Column(db.String(60), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, name, description=None):
        self.name = name
        self.slug = self.slugify(name)
        self.description = description
    
    @staticmethod
    def slugify(text):
        """Convert text to slug format."""
        text = text.lower()
        return re.sub(r'[^\w]+', '-', text).strip('-')
    
    @property
    def question_count(self):
        """Get the number of questions with this tag."""
        return self.questions.count()
    
    def __repr__(self):
        return f'<Tag {self.name}>'
