from . import db

class Component(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    amount = db.Column(db.Integer)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

class ProjectComponent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    component_id = db.Column(db.Integer, db.ForeignKey('component.id'))
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    amount = db.Column(db.Integer)