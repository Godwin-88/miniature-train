from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from .config import Config

# Initialize the database
db = SQLAlchemy()
migrate = Migrate()

#These are the database and migration instances. 
#They need to be initialized separately to ensure they can be accessed throughout the application.




def create_app(config_class=Config):
    # Initialize the Flask app
    app = Flask(__name__)
    
    # Load configurations from the config file
    app.config.from_object(config_class)

    # Initialize extensions with the app
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)  # Enable Cross-Origin Resource Sharing

    # Import and register blueprints
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # Additional initialization steps if required
    # e.g., logging, custom error handling

    return app

# Import the models after initializing the app to avoid circular imports
from . import models

'''Explanation:
Imports:

Flask: The core of your Flask application.
SQLAlchemy: For ORM (Object-Relational Mapping) to interact with the database.
Migrate: Flask-Migrate, which handles database migrations.
CORS: Handles Cross-Origin Resource Sharing, allowing your backend to interact with frontend apps on different domains.
Config: Configuration settings for the app, typically defined in a config.py file.
db and migrate:

These are the database and migration instances. They need to be initialized separately to ensure they can be accessed throughout the application.
create_app function:

This is a factory function that creates and configures the Flask app. It allows for better testing and flexibility, enabling different configurations for development, testing, and production environments.
app.config.from_object(config_class): Loads configurations from a Config class, which typically resides in a config.py file.
db.init_app(app): Binds the SQLAlchemy instance to the Flask app.
migrate.init_app(app, db): Binds the migration instance to the app and the database.
CORS(app): Enables CORS to allow cross-domain requests, useful when the frontend and backend are hosted separately.
Blueprints:

from .routes import main as main_blueprint: Imports the blueprint from the routes.py file.
app.register_blueprint(main_blueprint): Registers the blueprint with the app.
Import models:

The models are imported after the app is initialized to avoid circular imports. This way, the models are recognized by SQLAlchemy and Flask-Migrate.
This template provides a solid foundation for a scalable Flask application and can be extended with more features as needed.
'''