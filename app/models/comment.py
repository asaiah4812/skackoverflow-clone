from datetime import datetime
from app import db

class Comment(db.Model):
    """Comment model for storing comments on questions and answers."""
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Polymorphic association
    parent_type = db.Column(db.String(50))
    parent_id = db.Column(db.Integer)
    
    def __repr__(self):
        return f'<Comment {self.id}>'