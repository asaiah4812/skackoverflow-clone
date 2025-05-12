import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_moment import Moment
from flask_wtf.csrf import CSRFProtect
from config import config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'
mail = Mail()
moment = Moment()
csrf = CSRFProtect()

def create_app(config_name):
    """Application factory function."""
    app = Flask(__name__, static_folder='static')
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    csrf.init_app(app)
    
    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.questions import questions_bp
    from app.routes.answers import answers_bp
    from app.routes.users import users_bp
    from app.utils.filters import filters_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(questions_bp, url_prefix='/questions')
    app.register_blueprint(answers_bp, url_prefix='/answers')
    app.register_blueprint(users_bp, url_prefix='/users')
    app.register_blueprint(filters_bp)
    
    # Shell context processor
    @app.shell_context_processor
    def make_shell_context():
        from app.models.user import User
        from app.models.question import Question
        from app.models.answer import Answer
        from app.models.tag import Tag
        
        return {
            'db': db, 
            'User': User, 
            'Question': Question, 
            'Answer': Answer,
            'Tag': Tag
        }
    
    # Error handlers
    @app.errorhandler(404)
    def page_not_found(error):
        from flask import render_template
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(error):
        from flask import render_template
        return render_template('errors/500.html'), 500
    
    return app

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

@app.cli.command()
def deploy():
    """Run deployment tasks."""
    # Run database migrations
    from flask_migrate import upgrade
    upgrade()
    
    # Create or upgrade database
    db.create_all()
    
    # Create roles if using role-based authentication
    # Role.insert_roles()
    
    # Other deployment tasks as needed

if __name__ == '__main__':
    app.run(debug=True)
