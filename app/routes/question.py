from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import current_user, login_required
from app import db
from app.models.question import Question, QuestionVote
from app.models.tag import Tag
from app.models.answer import Answer, Comment
from app.forms.question import QuestionForm, TagForm
from app.forms.answer import AnswerForm, CommentForm
import os
from werkzeug.utils import secure_filename
from datetime import datetime

questions_bp = Blueprint('questions', __name__)

@questions_bp.route('/ask', methods=['GET', 'POST'])
@login_required
def ask():
    """Create a new question."""
    form = QuestionForm()
    
    # Set up tag choices
    form.tags.choices = [(tag.id, tag.name) for tag in Tag.query.order_by(Tag.name).all()]
    
    if form.validate_on_submit():
        question = Question(
            title=form.title.data,
            body=form.body.data,
            user_id=current_user.id
        )
        
        # Add selected tags
        for tag_id in form.tags.data:
            tag = Tag.query.get(tag_id)
            if tag:
                question.tags.append(tag)
        
        # Handle file upload if there is one
        if form.attachments.data:
            file = form.attachments.data
            if file:
                filename = secure_filename(file.filename)
                # Create unique filename to avoid overwrite
                unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'questions', unique_filename)
                
                # Ensure directory exists
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                file.save(file_path)
                # Add file reference to question if needed
                # question.attachment_path = f"uploads/questions/{unique_filename}"
        
        db.session.add(question)
        db.session.commit()
        flash('Your question has been posted!', 'success')
        return redirect(url_for('questions.view', question_id=question.id))
    
    return render_template('questions/create.html', title='Ask a Question', form=form)

@questions_bp.route('/<int:question_id>', methods=['GET'])
def view(question_id):
    """View a single question and its answers."""
    question = Question.query.get_or_404(question_id)
    
    # Increment view count
    question.views += 1
    db.session.commit()
    
    # Forms for answers and comments
    answer_form = AnswerForm()
    comment_form = CommentForm()
    
    # Get answers, sorted by score and acceptance status
    answers = Answer.query.filter_by(question_id=question.id)\
        .order_by(Answer.is_accepted.desc())\
        .all()
    
    # Check if user has voted on this question
    user_vote = None
    if current_user.is_authenticated:
        user_vote = QuestionVote.query.filter_by(
            user_id=current_user.id,
            question_id=question.id
        ).first()
    
    return render_template('questions/view.html',
                          title=question.title,
                          question=question,
                          answers=answers,
                          answer_form=answer_form,
                          comment_form=comment_form,
                          user_vote=user_vote)

@questions_bp.route('/<int:question_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(question_id):
    """Edit an existing question."""
    question = Question.query.get_or_404(question_id)
    
    # Check if current user is the author
    if question.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    
    form = QuestionForm()
    form.tags.choices = [(tag.id, tag.name) for tag in Tag.query.order_by(Tag.name).all()]
    
    if form.validate_on_submit():
        question.title = form.title.data
        question.body = form.body.data
        
        # Update tags
        question.tags = []
        for tag_id in form.tags.data:
            tag = Tag.query.get(tag_id)
            if tag:
                question.tags.append(tag)
        
        db.session.commit()
        flash('Your question has been updated!', 'success')
        return redirect(url_for('questions.view', question_id=question.id))
    
    # Pre-populate form
    if request.method == 'GET':
        form.title.data = question.title
        form.body.data = question.body
        form.tags.data = [tag.id for tag in question.tags]
    
    return render_template('questions/edit.html', title='Edit Question', form=form, question=question)

@questions_bp.route('/<int:question_id>/delete', methods=['POST'])
@login_required
def delete(question_id):
    """Delete a question."""
    question = Question.query.get_or_404(question_id)
    
    # Check if current user is the author or admin
    if question.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    
    db.session.delete(question)
    db.session.commit()
    flash('Your question has been deleted!', 'success')
    return redirect(url_for('main.index'))

@questions_bp.route('/<int:question_id>/vote/<int:value>', methods=['POST'])
@login_required
def vote(question_id, value):
    """Vote on a question (upvote or downvote)."""
    # Validate vote value (1 for upvote, -1 for downvote)
    if value not in [1, -1]:
        abort(400)
    
    question = Question.query.get_or_404(question_id)
    
    # Check if user has already voted
    existing_vote = QuestionVote.query.filter_by(
        user_id=current_user.id,
        question_id=question_id
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
        vote = QuestionVote(
            user_id=current_user.id,
            question_id=question_id,
            value=value
        )
        db.session.add(vote)
        message = 'Vote recorded'
    
    db.session.commit()
    flash(message, 'success')
    return redirect(url_for('questions.view', question_id=question_id))

@questions_bp.route('/tags', methods=['GET'])
def tags():
    """List all available tags."""
    tags = Tag.query.order_by(Tag.name).all()
    return render_template('questions/tags.html', title='Tags', tags=tags)

@questions_bp.route('/tags/new', methods=['GET', 'POST'])
@login_required
def create_tag():
    """Create a new tag."""
    form = TagForm()
    
    if form.validate_on_submit():
        # Check if tag already exists
        existing_tag = Tag.query.filter_by(name=form.name.data).first()
        if existing_tag:
            flash('A tag with that name already exists.', 'warning')
            return redirect(url_for('questions.tags'))
        
        tag = Tag(
            name=form.name.data,
            description=form.description.data
        )
        db.session.add(tag)
        db.session.commit()
        flash('Tag created successfully!', 'success')
        return redirect(url_for('questions.tags'))
    
    return render_template('questions/create_tag.html', title='Create Tag', form=form)

@questions_bp.route('/tags/<int:tag_id>', methods=['GET'])
def tag_questions(tag_id):
    """List questions with a specific tag."""
    tag = Tag.query.get_or_404(tag_id)
    page = request.args.get('page', 1, type=int)
    
    questions = Question.query.filter(Question.tags.contains(tag))\
        .order_by(Question.created_at.desc())\
        .paginate(page=page, per_page=current_app.config['POSTS_PER_PAGE'])
    
    return render_template('questions/tag_questions.html',
                          title=f'Questions tagged: {tag.name}',
                          tag=tag,
                          questions=questions)