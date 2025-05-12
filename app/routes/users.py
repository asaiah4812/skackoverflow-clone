from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import current_user, login_required
from app import db
from app.models.user import User
from app.models.question import Question
from app.models.answer import Answer
from app.forms.user import UpdateProfileForm
from datetime import datetime
import os
from werkzeug.utils import secure_filename

users_bp = Blueprint('users', __name__)

@users_bp.route('/<username>')
def profile(username):
    """Display user profile."""
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    
    # Get user's questions
    questions = Question.query.filter_by(user_id=user.id)\
        .order_by(Question.created_at.desc())\
        .paginate(page=page, per_page=current_app.config.get('POSTS_PER_PAGE', 10))
    
    # Get user's answers
    answers = Answer.query.filter_by(user_id=user.id)\
        .order_by(Answer.created_at.desc())\
        .paginate(page=page, per_page=current_app.config.get('POSTS_PER_PAGE', 10))
    
    return render_template('users/profile.html',
                          title=f"{user.username}'s Profile",
                          user=user,
                          questions=questions,
                          answers=answers)

@users_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """User settings page."""
    form = UpdateProfileForm()
    
    if form.validate_on_submit():
        # Update user information
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.bio = form.bio.data
        current_user.location = form.location.data
        current_user.website = form.website.data
        
        # Handle profile image upload
        if form.profile_image.data:
            file = form.profile_image.data
            if file:
                filename = secure_filename(file.filename)
                # Create unique filename to avoid overwrite
                unique_filename = f"{current_user.username}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{filename}"
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'profiles', unique_filename)
                
                # Ensure directory exists
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                file.save(file_path)
                current_user.profile_image = f"uploads/profiles/{unique_filename}"
        
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('users.profile', username=current_user.username))
    
    # Pre-populate form
    if request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.bio.data = current_user.bio
        form.location.data = current_user.location
        form.website.data = current_user.website
    
    return render_template('users/settings.html', title='Settings', form=form)
