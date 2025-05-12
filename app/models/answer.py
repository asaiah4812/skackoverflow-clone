from datetime import datetime
from app import db
from markdown import markdown
import bleach

class Answer(db.Model):
    """Answer model for storing answer related details."""
    __tablename__ = 'answers'
    
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    body_html = db.Column(db.Text)  # Stored HTML representation of the markdown body
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_accepted = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    
    # Relationships
    comments = db.relationship('Comment', backref='answer', lazy='dynamic',
                              cascade='all, delete-orphan',
                              primaryjoin='Comment.answer_id == Answer.id')
    votes = db.relationship('AnswerVote', backref='answer', lazy='dynamic',
                           cascade='all, delete-orphan')
    
    @property
    def score(self):
        """Calculate score based on upvotes/downvotes."""
        upvotes = AnswerVote.query.filter_by(answer_id=self.id, value=1).count()
        downvotes = AnswerVote.query.filter_by(answer_id=self.id, value=-1).count()
        return upvotes - downvotes
    
    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        """Generate HTML representation of the markdown-formatted answer body."""
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p', 'img']
        allowed_attrs = {'a': ['href', 'title'],
                         'abbr': ['title'],
                         'acronym': ['title'],
                         'img': ['src', 'alt']}
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, attributes=allowed_attrs, strip=True))
    
    def __repr__(self):
        return f'<Answer {self.id} for Question {self.question_id}>'

# Event listener for Answer.body changes
db.event.listen(Answer.body, 'set', Answer.on_changed_body)

class AnswerVote(db.Model):
    """Model for tracking votes on answers."""
    __tablename__ = 'answer_votes'
    
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer, nullable=False)  # 1 for upvote, -1 for downvote
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    answer_id = db.Column(db.Integer, db.ForeignKey('answers.id'), nullable=False)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'answer_id', name='user_answer_vote_constraint'),)
    
    def __repr__(self):
        return f'<AnswerVote {self.user_id} -> {self.answer_id}: {self.value}>'

class Comment(db.Model):
    """Comment model for both questions and answers."""
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=True)
    answer_id = db.Column(db.Integer, db.ForeignKey('answers.id'), nullable=True)
    
    def __repr__(self):
        return f'<Comment {self.id}>'