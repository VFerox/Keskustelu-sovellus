from flask import Flask
from os import path
from flask_login import LoginManager
from .database import init_app, init_db
import os

DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev'
    
    # Initialize database
    init_app(app)
    
    # Initialize login manager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    
    from .views import views
    from .auth import auth
    
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    
    from .models import User
    
    @login_manager.user_loader
    def load_user(id):
        return User.get(int(id))
    

    create_database(app)
    
    return app

def create_database(app):

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, DB_NAME)
    
  
    if not os.path.exists(db_path):
        with app.app_context():
            init_db()
            print("Created Database!")