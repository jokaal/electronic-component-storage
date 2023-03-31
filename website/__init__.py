from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import json, os

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
json_url = os.path.join(os.path.dirname(SITE_ROOT), 'config.json')
config = json.load(open(json_url))
db = SQLAlchemy()

DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'qwerty'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}' # f'mysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_SERVER}/{DB_NAME}'
    db.init_app(app)

    from .views.views import views
    from .views.components import components
    from .views.projects import projects

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(components, url_prefix="/components")
    app.register_blueprint(projects, url_prefix="/projects")

    from .database.models import Component, Project, ProjectComponent

    with app.app_context():
        if config['database']['dropDatabase']:
            db.drop_all()
        db.create_all()

    return app