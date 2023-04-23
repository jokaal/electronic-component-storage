from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, abort
from ..database.models import Project, ProjectComponent, Component
from .. import db, config
from ..helper import projectErrors, findMax, allowedFile
import json, csv

# Creating Blueprint, URL prefix is '/components'
projects = Blueprint('projects', __name__)

# Number of results to show per page as per configuration
per_page = config['settings']['resultsPerPage']

# Maps list() function as handler for address '/projects'
# Used to render a list of all projects
# Queries projects based on search and how many to show per page
# Renders ./templates/projects/projects.html template with query result
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

# Maps create() function as handler for address '/projects/create'
# Renders ./templates/projects/functions/create_project.html
@projects.route('/create', methods=['GET', 'POST'])
def create():

    # Referrer allows saving search but it's lost after another function and creates an infinite loop.
    referrer = None
    list = ['edit','create','view','build','project-component']
    if request.referrer and not any([x in request.referrer for x in list]): # https://stackoverflow.com/questions/3389574/check-if-multiple-strings-exist-in-another-string
        referrer=request.referrer


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

    return render_template('projects/functions/create_project.html', referrer=referrer)

# Maps view() function as handler for address '/projects/view/<id>'
# Renders ./templates/projects/functions/view_project.html
@projects.route('/view/<id>')
def view(id):
    project = Project.query.get_or_404(id)
    projectComponents = ProjectComponent.query.filter_by(project_id=id)
    inProgressComponents = projectComponents.filter(ProjectComponent.build_amount.isnot(None)).all()

    buildInProgress = False
    if inProgressComponents:
        buildInProgress = True
    buildMax = findMax(projectComponents)

    # Referrer allows saving search but it's lost after another function and creates an infinite loop.
    referrer = None
    list = ['edit','create','view','build','project-component']
    if request.referrer and not any([x in request.referrer for x in list]): # https://stackoverflow.com/questions/3389574/check-if-multiple-strings-exist-in-another-string
        referrer=request.referrer

    return render_template('projects/functions/view_project.html', project=project, projectComponents=projectComponents, referrer=referrer, buildMax=buildMax, buildInProgress=buildInProgress)

# Maps edit() function as handler for address '/projects/edit/<id>'
# Renders ./templates/projects/functions/edit_project.html
@projects.route('/edit/<id>', methods=['GET', 'POST'])
def edit(id):
    project = Project.query.get_or_404(id)

    if request.method == 'POST':
        
        name = None if request.form.get('name') == '' else request.form.get('name') # Form returns an empty string if not filled but we need null for database
        
        project.name = name
        
        if not projectErrors(project):
            db.session.add(project)
            db.session.commit()
            flash(f'Project \'{name}\' has been saved!', category='success')
            return redirect(url_for('projects.view', id=id))

    return render_template('projects/functions/edit_project.html', project=project)

# Maps delete() function as handler for address '/projects/delete'
# Function is used for JavaScript functions found in '/static/custom.js'
@projects.route('/delete', methods=['POST'])
def delete():
    project = json.loads(request.data)
    projectId = project['projectId']
    project = Project.query.get_or_404(projectId)
    if project:
        db.session.delete(project)
        db.session.commit()
    return jsonify({}) # Function is used in static/custom.js

# Maps addProjectComponent() function as handler for address '/projects/project-component/add'
# Function is used for JavaScript functions found in '/static/custom.js'
@projects.route('/project-component/add', methods=['POST'])
def addProjectComponent():
    project = json.loads(request.data)
    projectId = project['projectId']
    if project:
        projectComponent = ProjectComponent(project_id=projectId)
        db.session.add(projectComponent)
        db.session.commit()
    return jsonify({}) # Function is used in static/custom.js

# Maps chooseProjectComponent() function as handler for address '/projects/project-component/<id>'
# Renders ./templates/projects/functions/choose_component.html
@projects.route('/project-component/<id>', methods=['GET', 'POST'])
def chooseProjectComponent(id):
    projectComponent = ProjectComponent.query.get_or_404(id)

    referrer = None
    if 'project-component' not in request.referrer:
        referrer=request.referrer

    search = None if request.args.get('search') == '' else request.args.get('search')
    page = request.args.get('page', 1, type=int)
    query = Component.query

    if search:
        #https://stackoverflow.com/questions/4926757/sqlalchemy-query-where-a-column-contains-a-substring
        if '*' in search or '_' in search:
            looking_for = search.replace('_', '__').replace('*', '%').replace('?', '_')
        else:
            looking_for = '%{0}%'.format(search)
        query = query.filter((Component.name.ilike(looking_for)) |
                              (Component.value.ilike(looking_for)) |
                                (Component.description.ilike(looking_for)))

    pagination = query.paginate(page=page, per_page=per_page) # Pagination tutorial (a bit out of date): https://www.digitalocean.com/community/tutorials/how-to-query-tables-and-paginate-data-in-flask-sqlalchemy#step-5-displaying-long-record-lists-on-multiple-pages

    return render_template('projects/functions/choose_component.html', pagination=pagination, search=search, projectComponent=projectComponent, project=projectComponent.project, referrer=referrer)

# Maps addProjectComponentId() function as handler for address '/projects/project-component/add-component'
# Function is used for JavaScript functions found in '/static/custom.js'
@projects.route('/project-component/add-component', methods=['POST'])
def addProjectComponentId():
    jsonData = json.loads(request.data)
    projectComponentId = jsonData['projectComponentId']
    componentId = jsonData['componentId']
    if projectComponentId and componentId:
        projectComponent = ProjectComponent.query.get(projectComponentId)
        projectComponent.component_id = componentId
        db.session.add(projectComponent)
        db.session.commit()
    return jsonify({}) # Function is used in static/custom.js

# Maps editProjectComponentAmount() function as handler for address '/projects/project-component/amount'
# Function is used for JavaScript functions found in '/static/custom.js'
@projects.route('/project-component/amount', methods=['POST'])
def editProjectComponentAmount():
    jsonData = json.loads(request.data)
    projectComponentId = jsonData['projectComponentId']
    amount = jsonData['amount']
    if projectComponentId and amount:
        projectComponent = ProjectComponent.query.get_or_404(projectComponentId)
        projectComponent.amount = amount
        db.session.add(projectComponent)
        db.session.commit()
    return jsonify({}) # Function is used in static/custom.js

# Maps editProjectComponentComment() function as handler for address '/projects/project-component/comment'
# Function is used for JavaScript functions found in '/static/custom.js'
@projects.route('/project-component/comment', methods=['POST'])
def editProjectComponentComment():
    jsonData = json.loads(request.data)
    projectComponentId = jsonData['projectComponentId']
    comment = jsonData['comment']
    if projectComponentId:
        projectComponent = ProjectComponent.query.get_or_404(projectComponentId)
        projectComponent.comment = comment
        db.session.add(projectComponent)
        db.session.commit()
    return jsonify({}) # Function is used in static/custom.js

# Maps deleteProjectComponent() function as handler for address '/projects/project-component/delete'
# Function is used for JavaScript functions found in '/static/custom.js'
@projects.route('/project-component/delete', methods=['POST'])
def deleteProjectComponent():
    jsonData = json.loads(request.data)
    projectComponentId = jsonData['projectComponentId']
    if projectComponentId:
        projectComponent = ProjectComponent.query.get_or_404(projectComponentId)
        db.session.delete(projectComponent)
        db.session.commit()
    return jsonify({}) # Function is used in static/custom.jss

# Maps build() function as handler for address '/projects/build/<id>'
# Renders ./templates/projects/functions/build_project.html
@projects.route('/build/<id>', methods=['GET','POST'])
def build(id):

    project = Project.query.get_or_404(id)
    projectComponents = ProjectComponent.query.filter_by(project_id=id)

    if request.method == 'POST':
        buildAmount = int(None if request.form.get('buildAmount') == '' else request.form.get('buildAmount'))
        buildMax = findMax(projectComponents)
        if not buildAmount or buildAmount > buildMax or buildAmount == 0:
            flash(f'Can\'t build project {buildAmount} times!', category='error')
            return render_template('projects/functions/view_project.html', project=project, projectComponents=projectComponents, buildMax=buildMax)
        
        for projectComponent in projectComponents:
            projectComponent.build_amount = projectComponent.amount * buildAmount
            db.session.add(projectComponent)
        db.session.commit()
                    
    inProgressComponents = projectComponents.filter(ProjectComponent.build_amount.isnot(None)).all()
    if len(inProgressComponents) != 0:
        return render_template('projects/functions/build_project.html', project=project, projectComponents=inProgressComponents)
    else:
        return abort(404)


@projects.route('/build/end', methods=['POST'])
def endBuild():
    project = json.loads(request.data)
    projectId = project['projectId']
    project = Project.query.get_or_404(projectId)
    if project:
        projectComponents = ProjectComponent.query.filter_by(project_id=project.id)
        for projectComponent in projectComponents:
            projectComponent.build_amount = None
        db.session.commit()
    return jsonify({}) # Function is used in static/custom.js

# Maps removeComponentsForBuild() function as handler for address '/projects/build'
# Renders ./templates/projects/functions/build_project.html
@projects.route('/project-component/build', methods=['POST'])
def removeComponentsForBuild():
    id = None if request.form.get('id') == '' else request.form.get('id')
    projectComponent = ProjectComponent.query.get_or_404(id)
    project = Project.query.get(projectComponent.project_id)
    projectComponents = ProjectComponent.query.filter_by(project_id=projectComponent.project.id)
    inProgressComponents = projectComponents.filter(ProjectComponent.build_amount.isnot(None)).all()

    # Check if project component has a value
    if not projectComponent.build_amount:
        return abort(404)

    # If there's not enough components in storage then flash an error (happens when building two projects at the same time)
    if projectComponent.build_amount > projectComponent.component.amount:
        flash(f'Can\'t have less than 0 components in storage!', category='error')
        return render_template('projects/functions/build_project.html', project=project, projectComponents=inProgressComponents)

    # First remove required amount from storage and set build_amount to null
    projectComponent.component.amount -= projectComponent.build_amount
    projectComponent.build_amount = None
    db.session.commit()

    # Check if any components left in build
    inProgressComponents = projectComponents.filter(ProjectComponent.build_amount.isnot(None)).all()
    if len(inProgressComponents) != 0:
        return render_template('projects/functions/build_project.html', project=project, projectComponents=inProgressComponents)
    else:
        buildMax = findMax(projectComponents)
        flash('Finished building project!', category='success')
        return render_template('projects/functions/view_project.html', project=project, projectComponents=projectComponents, buildMax=buildMax)
        
# Maps importFromBOM() function as handler for address '/projects/import/<id>'
# Renders ----
@projects.route('/import/<id>', methods=['GET', 'POST'])
def importFromBOM(id):
    
    components = []
    if request.method == 'POST': # https://flask.palletsprojects.com/en/2.2.x/patterns/fileuploads/
        if 'file' not in request.files:
            flash('No file part!', category='error')
        else:
            allowedExtensions = {'csv'}
            file = request.files['file']
            if file.filename == '':
                flash('No selected file!', category='error')
            else:
                if allowedFile(file.filename, allowedExtensions):
                    # TODO: Implement BOM importing
                    return
        
        
        return render_template('components/functions/import_components.html', components=components)