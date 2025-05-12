from app import create_app, db
import os
import traceback

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

with app.app_context():
    try:
        # Import models here to avoid circular imports
        from app.models.user import User
        from app.models.question import Question
        from app.models.answer import Answer
        from app.models.tag import Tag
        
        # Drop all tables and recreate them
        db.drop_all()
        db.create_all()
        
        print("Database tables created successfully!")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        traceback.print_exc()


