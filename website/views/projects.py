from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from ..database.models import Project, ProjectComponent
from .. import db, config
from ..helper import projectErrors, findMax
import json

projects = Blueprint('projects', __name__)
per_page = config['settings']['resultsPerPage']

@projects.route('/', methods=['GET', 'POST'])
def list():
    search = None if request.args.get('search') == '' else request.args.get('search')
    page = request.args.get('page', 1, type=int)
    query = Project.query
    
    if search:
        if '*' in search or '_' in search:
            looking_for = search.replace('_', '__').replace('*', '%').replace('?', '_')
        else:
            looking_for = '%{0}%'.format(search)
        query = Project.query.filter((Project.name.ilike(looking_for)))

    pagination = query.paginate(page=page, per_page=per_page)

    return render_template('projects/projects.html', pagination=pagination, search=search)

@projects.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        name = None if request.form.get('name') == '' else request.form.get('name') # Form return an empty string if not filled but we need null for database
        new_project = Project(name=name)
        
        if not projectErrors(new_project):
            db.session.add(new_project)
            db.session.commit()
            flash(f'Project \'{name}\' has been created!', category='success')
            return redirect(url_for('projects.view', id=new_project.id))
        else:
            return render_template('projects/functions/create_project.html', project=new_project)

    return render_template('projects/functions/create_project.html')

@projects.route('/view/<id>')
def view(id):
    project = Project.query.get(id)
    projectComponents = ProjectComponent.query.filter_by(project_id=id)

    buildMax = findMax(projectComponents)

    referrer = None
    if 'edit' and 'create' and f'projects/view/{id}' not in request.referrer: # Allows going back to search result but after editing search is lost
        referrer=request.referrer

    return render_template('projects/functions/view_project.html', project=project, projectComponents=projectComponents, referrer=referrer, buildMax=buildMax)

@projects.route('/edit/<id>', methods=['GET', 'POST'])
def edit(id):
    project = Project.query.get(id)

    if request.method == 'POST':
        
        name = None if request.form.get('name') == '' else request.form.get('name') # Form return an empty string if not filled but we need null for database
        
        project.name = name
        
        if not projectErrors(project):
            db.session.add(project)
            db.session.commit()
            flash(f'Project \'{name}\' has been saved!', category='success')
            return redirect(url_for('projects.view', id=id))

    return render_template('projects/functions/edit_project.html', project=project, referrer=request.referrer)


@projects.route('/delete', methods=['POST'])
def delete():
    project = json.loads(request.data)
    projectId = project['projectId']
    project = Project.query.get(projectId)
    if project:
        db.session.delete(project)
        db.session.commit()
    return jsonify({}) # Function is used in static/custom.js

@projects.route('/add-component-to-project', methods=['POST'])
def add_project_component():
    project = json.loads(request.data)
    projectId = project['projectId']
    if project:
        projectComponent = ProjectComponent(project_id=projectId)
        db.session.add(projectComponent)
        db.session.commit()
    return jsonify({}) # Function is used in static/custom.js