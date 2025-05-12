from flask import Blueprint, redirect, url_for, flash, request, abort, current_app
from flask_login import current_user, login_required
from app import db
from app.models.question import Question
from app.models.answer import Answer, AnswerVote, Comment
from app.forms.answer import AnswerForm, CommentForm
import os
from werkzeug.utils import secure_filename
from datetime import datetime

answers_bp = Blueprint('answers', __name__)

@answers_bp.route('/create/<int:question_id>', methods=['POST'])
@login_required
def create(question_id):
    """Create a new answer for a question."""
    question = Question.query.get_or_404(question_id)
    form = AnswerForm()
    
    if form.validate_on_submit():
        answer = Answer(
            body=form.body.data,
            user_id=current_user.id,
            question_id=question.id
        )
        
        # Handle file upload if there is one
        if form.attachments.data:
            file = form.attachments.data
            if file:
                filename = secure_filename(file.filename)
                # Create unique filename to avoid overwrite
                unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'answers', unique_filename)
                
                # Ensure directory exists
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                file.save(file_path)
                # Add file reference to answer if needed
                # answer.attachment_path = f"uploads/answers/{unique_filename}"
        
        db.session.add(answer)
        db.session.commit()
        flash('Your answer has been posted!', 'success')
    
    return redirect(url_for('questions.view', question_id=question.id))

@answers_bp.route('/<int:answer_id>/submit', methods=['POST'])
@login_required
def submit(answer_id):
    """Submit an answer to a question."""
    question = Question.query.get_or_404(question_id)
    form = AnswerForm()
    
    if form.validate_on_submit():
        answer = Answer(
            body=form.body.data,
            user_id=current_user.id,
            question_id=question.id
        )
        
        # Handle file upload if there is one
        if form.attachments.data:
            file = form.attachments.data
            if file:
                filename = secure_filename(file.filename)
                # Create unique filename to avoid overwrite
                unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'answers', unique_filename)
                
                # Ensure directory exists
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                file.save(file_path)
                # Add file reference to answer if needed
                # answer.attachment_path = f"uploads/answers/{unique_filename}"
        
        db.session.add(answer)
        db.session.commit()
        flash('Your answer has been posted!', 'success')
    
    return redirect(url_for('questions.view', question_id=question.id))

@answers_bp.route('/<int:answer_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(answer_id):
    """Edit an existing answer."""
    answer = Answer.query.get_or_404(answer_id)
    question = answer.question
    
    # Check if current user is the author
    if answer.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    
    form = AnswerForm()
    
    if form.validate_on_submit():
        answer.body = form.body.data
        db.session.commit()
        flash('Your answer has been updated!', 'success')
        return redirect(url_for('questions.view', question_id=question.id))
    
    # Pre-populate form
    if request.method == 'GET':
        form.body.data = answer.body
    
    return redirect(url_for('questions.view', question_id=question.id, _anchor=f'answer-{answer.id}-edit'))

@answers_bp.route('/<int:answer_id>/delete', methods=['POST'])
@login_required
def delete(answer_id):
    """Delete an answer."""
    answer = Answer.query.get_or_404(answer_id)
    question_id = answer.question_id
    
    # Check if current user is the author or admin
    if answer.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    
    db.session.delete(answer)
    db.session.commit()
    flash('Your answer has been deleted!', 'success')
    return redirect(url_for('questions.view', question_id=question_id))

@answers_bp.route('/<int:answer_id>/accept', methods=['POST'])
@login_required
def accept(answer_id):
    """Mark an answer as accepted."""
    answer = Answer.query.get_or_404(answer_id)
    question = Question.query.get_or_404(answer.question_id)
    
    # Check if current user is the question author
    if question.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    
    # Remove accepted status from any previously accepted answer
    previously_accepted = Answer.query.filter_by(
        question_id=question.id,
        is_accepted=True
    ).first()
    
    if previously_accepted:
        previously_accepted.is_accepted = False
    
    # Mark this answer as accepted
    answer.is_accepted = True
    question.is_solved = True
    db.session.commit()
    flash('Answer has been marked as accepted!', 'success')
    return redirect(url_for('questions.view', question_id=question.id))

@answers_bp.route('/<int:answer_id>/vote/<int:value>', methods=['POST'])
@login_required
def vote(answer_id, value):
    """Vote on an answer (upvote or downvote)."""
    # Validate vote value (1 for upvote, -1 for downvote)
    if value not in [1, -1]:
        abort(400)
    
    answer = Answer.query.get_or_404(answer_id)
    question_id = answer.question_id
    
    # Check if user has already voted
    existing_vote = AnswerVote.query.filter_by(
        user_id=current_user.id,
        answer_id=answer_id
    ).first()
    
    if existing_vote:
        if existing_vote.value == value:
            # Remove vote if clicking same button again
            db.session.delete(existing_vote)
            message = 'Vote removed'
        else:
            # Change vote if clicking different button
            existing_vote.value = value
            message = 'Vote changed'
    else:
        # Add new vote
        vote = AnswerVote(
            user_id=current_user.id,
            answer_id=answer_id,
            value=value
        )
        db.session.add(vote)
        message = 'Vote recorded'
    
    db.session.commit()
    flash(message, 'success')
    return redirect(url_for('questions.view', question_id=question_id))

@answers_bp.route('/<int:answer_id>/comment', methods=['POST'])
@login_required
def add_comment(answer_id):
    """Add a comment to an answer."""
    answer = Answer.query.get_or_404(answer_id)
    question_id = answer.question_id
    form = CommentForm()
    
    if form.validate_on_submit():
        comment = Comment(
            body=form.body.data,
            user_id=current_user.id,
            answer_id=answer_id
        )
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been added!', 'success')
    
    return redirect(url_for('questions.view', question_id=question_id))
