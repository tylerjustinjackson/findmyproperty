from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

# Initialize extensions
db = SQLAlchemy()
login = LoginManager()
login.login_view = "routes.login"


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions with app
    db.init_app(app)
    login.init_app(app)

    # Import routes and register them with app
    from app.routes import routes_bp

    app.register_blueprint(routes_bp)

    # Create database tables
    with app.app_context():
        from app import models

        db.create_all()

    return app
