from datetime import datetime
from app import db
from markdown import markdown
import bleach

# Many-to-Many relationship between questions and tags
question_tags = db.Table('question_tags',
    db.Column('question_id', db.Integer, db.ForeignKey('questions.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
)

class Question(db.Model):
    """Question model for storing question related details."""
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    body = db.Column(db.Text, nullable=False)
    body_html = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    views = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    tags = db.relationship('Tag', secondary=question_tags, 
                          backref=db.backref('questions', lazy='dynamic'))
    answers = db.relationship('Answer', backref='question', lazy='dynamic',
                             cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='question', lazy='dynamic',
                              cascade='all, delete-orphan',
                              primaryjoin='Comment.question_id == Question.id')
    votes = db.relationship('QuestionVote', backref='question', lazy='dynamic',
                           cascade='all, delete-orphan')
    
    @property
    def score(self):
        """Calculate score based on upvotes/downvotes."""
        from app.models.question import QuestionVote
        upvotes = QuestionVote.query.filter_by(question_id=self.id, value=1).count()
        downvotes = QuestionVote.query.filter_by(question_id=self.id, value=-1).count()
        return upvotes - downvotes
    
    @property
    def answer_count(self):
        """Get the number of answers for this question."""
        return self.answers.count()
    
    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        """Generate HTML representation of the markdown-formatted question body."""
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
        return f'<Question {self.id}>'

# Event listener for Question.body changes
db.event.listen(Question.body, 'set', Question.on_changed_body)

class QuestionVote(db.Model):
    """Model for tracking votes on questions."""
    __tablename__ = 'question_votes'
    
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer, nullable=False)  # 1 for upvote, -1 for downvote
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'question_id', name='user_question_vote_constraint'),)
    
    def __repr__(self):
        return f'<QuestionVote {self.user_id} -> {self.question_id}: {self.value}>'
