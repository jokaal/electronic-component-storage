from .. import db
from sqlalchemy.sql import func

class Component(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255))
    value = db.Column(db.String(255))
    description = db.Column(db.Text)
    amount = db.Column(db.Integer, default=0, nullable=False)
    minimum_amount = db.Column(db.Integer)
    url = db.Column(db.String(255))
    projects = db.Relationship('ProjectComponent', backref='component')
    
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    components = db.Relationship('ProjectComponent', backref='project', passive_deletes=True)

class ProjectComponent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    component_id = db.Column(db.Integer, db.ForeignKey('component.id'), nullable=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id', ondelete='CASCADE'), nullable=False)
    amount = db.Column(db.Integer, default=1, nullable=False)
    build_amount = db.Column(db.Integer, default=None)
    comment = db.Column(db.String(255), default=None)