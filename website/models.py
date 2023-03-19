from . import db

class Component(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    location = db.Column(db.String)
    value = db.Column(db.String)
    description = db.Column(db.Text)
    amount = db.Column(db.Integer, nullable=False, default=0)
    minimum_amount = db.Column(db.Integer)
    url = db.Column(db.String)
    
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

class ProjectComponent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    component_id = db.Column(db.Integer, db.ForeignKey('component.id'))
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    amount = db.Column(db.Integer)