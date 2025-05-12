from flask import Blueprint, render_template, request, current_app
from app.models.question import Question
from app.models.tag import Tag
from app.forms.question import SearchForm, QuestionFilterForm
from sqlalchemy import desc, func

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Render the home page with recent questions."""
    page = request.args.get('page', 1, type=int)
    search_form = SearchForm()
    filter_form = QuestionFilterForm()
    
    # Set up tag choices for filter form
    try:
        tags = Tag.query.order_by(Tag.name).all()
        filter_form.tags.choices = [(tag.id, tag.name) for tag in tags]
    except Exception as e:
        current_app.logger.error(f"Error loading tags: {str(e)}")
        filter_form.tags.choices = []
    
    # Get filter parameters
    selected_tags = request.args.getlist('tags', type=int)
    sort_by = request.args.get('sort_by', 'recent')
    
    # Debug output
    current_app.logger.info(f"Fetching questions with sort_by={sort_by}, selected_tags={selected_tags}")
    
    # Base query - simplify to just get all questions first
    query = Question.query.order_by(Question.created_at.desc())
    
    try:
        # Count total questions for debugging
        total_count = query.count()
        current_app.logger.info(f"Total questions in database: {total_count}")
        
        # Paginate results
        questions = query.paginate(
            page=page,
            per_page=current_app.config.get('POSTS_PER_PAGE', 10),
            error_out=False
        )
        
        # Get top tags for sidebar
        top_tags = Tag.query.limit(10).all()
        
        # Calculate counts for sidebar
        total_questions = Question.query.count()
        
        current_app.logger.info(f"Loaded {len(questions.items) if questions else 0} questions for page {page}")
        
    except Exception as e:
        current_app.logger.error(f"Error querying database: {str(e)}")
        questions = None
        top_tags = []
        total_questions = 0
        unanswered_count = 0
        popular_count = 0
    
    return render_template('main/index.html',
                           title='Home',
                           questions=questions,
                           search_form=search_form,
                           filter_form=filter_form,
                           selected_tags=selected_tags,
                           sort_by=sort_by,
                           top_tags=top_tags,
                           total_questions=total_questions,
                           unanswered_count=0,
                           popular_count=0)

@main_bp.route('/about')
def about():
    """Render the about page."""
    return render_template('main/about.html', title='About')

@main_bp.route('/search')
def search():
    """Search for questions."""
    search_form = SearchForm()
    query = request.args.get('query', '')
    page = request.args.get('page', 1, type=int)
    
    if query:
        try:
            # Search in question titles and bodies
            search_results = Question.query.filter(
                (Question.title.contains(query)) | 
                (Question.body.contains(query))
            ).order_by(desc(Question.created_at)).paginate(
                page=page,
                per_page=current_app.config['POSTS_PER_PAGE'],
                error_out=False
            )
        except Exception:
            search_results = None
    else:
        search_results = None
    
    return render_template('main/search.html',
                           title='Search Results',
                           search_form=search_form,
                           query=query,
                           results=search_results)

@main_bp.route('/debug')
def debug():
    """Debug route to check database contents."""
    try:
        # Count questions
        question_count = Question.query.count()
        
        # Get all questions
        questions = Question.query.all()
        
        # Format question data
        question_data = []
        for q in questions:
            question_data.append({
                'id': q.id,
                'title': q.title,
                'user_id': q.user_id,
                'created_at': q.created_at,
                'tags': [t.name for t in q.tags]
            })
        
        # Count users
        user_count = User.query.count()
        
        # Count tags
        tag_count = Tag.query.count()
        
        return {
            'question_count': question_count,
            'questions': question_data,
            'user_count': user_count,
            'tag_count': tag_count
        }
    except Exception as e:
        return {'error': str(e)}
