from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import json, os

# Variables used to find the configuration file
SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
json_url = os.path.join(os.path.dirname(SITE_ROOT), 'config.json')

# Application configuration
config = json.load(open(json_url))

# Database variable used in controllers
db = SQLAlchemy()

# Function used to create the Flask application instance
# Returns object of type Flask
def create_app() -> Flask:

    # Creating instance
    app = Flask(__name__)

    # Importing Blueprints
    from .views.views import views
    from .views.components import components
    from .views.projects import projects

    # Registering Blueprints
    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(components, url_prefix="/components")
    app.register_blueprint(projects, url_prefix="/projects")

    # Database secret key
    app.config['SECRET_KEY'] = 'secret'

    # Database URL setup
    DB_NAME = config['database']['dbName']
    if config['database']['useSQLite']:
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    else:
        DB_USERNAME = config['database']['dbUsername']
        DB_PASSWORD = config['database']['dbPassword']
        DB_SERVER = config['database']['dbServer']
        app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_SERVER}/{DB_NAME}'

    # Establishing database connection
    db.init_app(app)

    # Importing database models
    from .database.models import Component, Project, ProjectComponent

    # Filling database
    with app.app_context():
        if config['database']['dropDatabase']:
            db.drop_all()
        db.create_all()

    return app