from . import db
from sqlalchemy.sql import func

class Component(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    location = db.Column(db.String)
    value = db.Column(db.String)
    description = db.Column(db.Text)
    amount = db.Column(db.Integer, default=0, nullable=False)
    minimum_amount = db.Column(db.Integer)
    url = db.Column(db.String)
    
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    is_finished = db.Column(db.Boolean, default=False, nullable=False)

class ProjectComponent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    component_id = db.Column(db.Integer, db.ForeignKey('component.id'))
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    amount = db.Column(db.Integer)