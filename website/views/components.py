from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from ..database.models import Component, ProjectComponent
from .. import db, config
from ..helper import componentErrors, allowedFile
import json

# Creating Blueprint, URL prefix is '/components'
components = Blueprint('components', __name__)

# Number of results to show per page as per configuration
per_page = config['settings']['resultsPerPage']

# Maps list() function as handler for address '/components'
# Used to render a list of all components
# Queries components based on search and how many to show per page
# Renders ./templates/components/components.html template with query result
@components.route('/', methods=['GET', 'POST'])
def list():
    search = None if request.args.get('search') == '' else request.args.get('search')
    page = request.args.get('page', 1, type=int)
    query = Component.query

    if search:
        # https://stackoverflow.com/questions/4926757/sqlalchemy-query-where-a-column-contains-a-substring
        if '*' in search or '_' in search:
            looking_for = search.replace('_', '__').replace('*', '%').replace('?', '_')
        else:
            looking_for = '%{0}%'.format(search)
        query = query.filter((Component.name.ilike(looking_for)) |
                              (Component.value.ilike(looking_for)) |
                                (Component.description.ilike(looking_for)))

    pagination = query.paginate(page=page, per_page=per_page) # Pagination tutorial (a bit out of date): https://www.digitalocean.com/community/tutorials/how-to-query-tables-and-paginate-data-in-flask-sqlalchemy#step-5-displaying-long-record-lists-on-multiple-pages
    
    return render_template('components/components.html', pagination=pagination, search=search)

# Maps add() function as handler for address '/components/add'
# Renders ./templates/components/functions/add_component.html
@components.route('/add', methods=['GET', 'POST'])
def add():

    # Referrer allows saving search but it's lost after another function and creates an infinite loop.
    referrer = None
    list = ['edit','add','view','remove']
    if request.referrer and not any([x in request.referrer for x in list]): # https://stackoverflow.com/questions/3389574/check-if-multiple-strings-exist-in-another-string
        referrer=request.referrer

    if request.method == 'POST':
        name = None if request.form.get('name') == '' else request.form.get('name') # Form return an empty string if not filled but we need null for database
        location = None if request.form.get('location') == '' else request.form.get('location')
        value = None if request.form.get('value') == '' else request.form.get('value')
        description = None if request.form.get('description') == '' else request.form.get('description')
        amount = None if request.form.get('amount') == '' else request.form.get('amount')
        minimumAmount = None if request.form.get('minimumAmount') == '' else request.form.get('minimumAmount')
        url = None if request.form.get('url') == '' else request.form.get('url')
        
        new_component = Component(name=name, location=location, value=value, 
                                  description=description, amount=amount, minimum_amount=minimumAmount, url=url)
        
        if not componentErrors(new_component):
            db.session.add(new_component)
            db.session.commit()
            flash(f'Component \'{name}\' has been added!', category='success')
            return redirect(url_for('components.list'))
        else:
            return render_template('components/functions/add_component.html', component=new_component)

    return render_template('components/functions/add_component.html', referrer=referrer)

# Maps import() function as handler for address '/components/import'
# Renders ./templates/components/functions/import_components.html
@components.route('/import', methods=['GET', 'POST'])
def importComponents():
    referrer = None
    list = ['edit','add','view','remove','import']
    if request.referrer and not any([x in request.referrer for x in list]): # https://stackoverflow.com/questions/3389574/check-if-multiple-strings-exist-in-another-string
        referrer=request.referrer

    components = []
    if request.method == 'POST': # https://flask.palletsprojects.com/en/2.2.x/patterns/fileuploads/
        if 'file' not in request.files:
            flash('No file part!', category='error')
        else:
            allowedExtensions = {'json'}
            file = request.files['file']
            if file.filename == '':
                flash('No selected file!', category='error')
            else:
                if file and allowedFile(file.filename, allowedExtensions):
                    # Check if json has components
                    jsonData = json.loads(file.read())
                    componentsField = jsonData.get('components')
                    if componentsField:
                        
                        componentAmountError = 0
                        componentFieldError = 0

                        # Go through every component
                        for jsonComponent in jsonData['components']:
                            
                            name = jsonComponent.get('name')
                            # Check that required fields are found
                            if name:           
                                amount = jsonComponent.get('amount')
                                location = jsonComponent.get('location')
                                description = jsonComponent.get('description')
                                value = jsonComponent.get('value')
                                minimumAmount = jsonComponent.get('minimumAmount')
                                url = jsonComponent.get('url')

                                if (amount and amount < 0) or (minimumAmount and minimumAmount < 0):
                                    componentAmountError += 1
                                else:
                                    component = Component(name=name, location=location, value=value, 
                                                          description=description, amount=amount, minimum_amount=minimumAmount, url=url)
                                    components.append(component)
                            else:
                                componentFieldError += 1
                        errorMsg = []
                        if componentAmountError > 0:
                            errorMsg.append(f'Failed to import {componentAmountError} component(s) because their amount or minimum amount are less than 0')
                        if componentFieldError > 0:
                            errorMsg.append(f'Failed to import {componentFieldError} component(s) because they are missing the required field(s)')
                        if errorMsg:
                            flash(' & '.join(errorMsg), category='error')
                    else:
                        flash('Incorrect formatting! Couldn\'t find the \"components\" field.', category='error')
    return render_template('components/functions/import_components.html', components=components, referrer=referrer)

# Maps importConfirmed() function as handler for address '/components/import/confirm'
# Renders ./templates/components/components.html
@components.route('/import/confirm', methods=['POST'])
def importConfirmed():

    names = request.form.getlist('name')
    values = request.form.getlist('value')
    descriptions = request.form.getlist('description')
    locations = request.form.getlist('location')
    amounts = request.form.getlist('amount')
    minimumAmounts = request.form.getlist('minimumAmount')
    urls = request.form.getlist('url')

    for i in range(len(names)):
        name =  names[i]
        value = None if values[i] == 'None' else values[i]
        description = None if descriptions[i] == 'None' else descriptions[i]
        location = None if locations[i] == 'None' else locations[i]
        amount = None if amounts[i] == 'None' else amounts[i]
        minimumAmount = None if minimumAmounts[i] == 'None' else minimumAmounts[i]
        url = None if urls[i] == 'None' else urls[i]

        new_component = Component(name=name, location=location, value=value, 
                                  description=description, amount=amount, minimum_amount=minimumAmount, url=url)
        
        if not componentErrors(new_component):
            db.session.add(new_component)
            db.session.commit()

    return redirect(url_for('components.list'))

# Maps addProjectComponent() function as handler for address '/components/add/projectComponent/<id>'
# Renders ./templates/projects/functions/view_project.html
@components.route('/add/projectComponent/<id>', methods=['GET', 'POST'])
def addProjectComponent(id):
    projectComponent = ProjectComponent.query.get_or_404(id)

    # Referrer allows saving search but it's lost after another function and creates an infinite loop.
    referrer = None
    list = ['edit','add','view','remove']
    if request.referrer and not any([x in request.referrer for x in list]): # https://stackoverflow.com/questions/3389574/check-if-multiple-strings-exist-in-another-string
        referrer=request.referrer

    if request.method == 'POST':
        name = None if request.form.get('name') == '' else request.form.get('name') # Form return an empty string if not filled but we need null for database
        location = None if request.form.get('location') == '' else request.form.get('location')
        value = None if request.form.get('value') == '' else request.form.get('value')
        description = None if request.form.get('description') == '' else request.form.get('description')
        amount = None if request.form.get('amount') == '' else request.form.get('amount')
        minimumAmount = None if request.form.get('minimumAmount') == '' else request.form.get('minimumAmount')
        url = None if request.form.get('url') == '' else request.form.get('url')
        
        new_component = Component(name=name, location=location, value=value, 
                                  description=description, amount=amount, minimum_amount=minimumAmount, url=url)
        
        if not componentErrors(new_component):
            db.session.add(new_component)
            db.session.flush()
            projectComponent.component_id = new_component.id
            db.session.add(projectComponent)
            db.session.commit()
            flash(f'Component \'{name}\' has been added and selected for project \'{projectComponent.project.name}\'!', category='success')
            return redirect(url_for('projects.view', id=projectComponent.project_id))
        else:
            return render_template('components/functions/add_component.html', component=new_component)

    return render_template('components/functions/add_component.html', referrer=referrer)

# Maps view() function as handler for address '/components/view/<id>'
# Renders ./templates/components/functions/view_component.html
@components.route('/view/<id>')
def view(id):
    component = Component.query.get_or_404(id)

    # Referrer allows saving search but it's lost after another function and creates an infinite loop.
    referrer = None
    list = ['edit','add','components/view','remove']
    if request.referrer and not any([x in request.referrer for x in list]): # https://stackoverflow.com/questions/3389574/check-if-multiple-strings-exist-in-another-string
        referrer=request.referrer

    return render_template('components/functions/view_component.html', component=component, referrer=referrer)

# Maps edit() function as handler for address '/components/edit/<id>'
# Renders ./templates/components/functions/edit_component.html
@components.route('/edit/<id>', methods=['GET', 'POST'])
def edit(id):
    component = Component.query.get_or_404(id)

    if request.method == 'POST':
        
        name = None if request.form.get('name') == '' else request.form.get('name') # Form return an empty string if not filled but we need null for database
        location = None if request.form.get('location') == '' else request.form.get('location')
        value = None if request.form.get('value') == '' else request.form.get('value')
        description = None if request.form.get('description') == '' else request.form.get('description')
        amount = None if request.form.get('amount') == '' else request.form.get('amount')
        minimumAmount = None if request.form.get('minimumAmount') == '' else request.form.get('minimumAmount')
        url = None if request.form.get('url') == '' else request.form.get('url')
        
        component.name = name
        component.location = location
        component.value = value
        component.description = description
        component.amount = amount
        component.minimum_amount = minimumAmount
        component.url = url
        
        if not componentErrors(component):
            db.session.add(component)
            db.session.commit()
            flash(f'Component \'{name}\' has been saved!', category='success')
            return redirect(url_for('components.view', id=id))

    return render_template('components/functions/edit_component.html', component=component)

# Maps delete() function as handler for address '/components/delete'
# Function is used for JavaScript functions found in '/static/custom.js'
@components.route('/delete', methods=['POST'])
def delete():
    component = json.loads(request.data)
    componentId = component['componentId']
    component = Component.query.get_or_404(componentId)
    if component:
        ProjectComponent.query.filter_by(component_id=componentId).delete() # Removes components from project
        db.session.delete(component)
        db.session.commit()
    return jsonify({}) # Function is used in static/custom.js

# Maps addOne() function as handler for address '/components/add-one'
# Function is used for JavaScript functions found in '/static/custom.js'
@components.route('/add-one', methods=['POST'])
def addOne():
    component = json.loads(request.data)
    componentId = component['componentId']
    component = Component.query.get_or_404(componentId)
    if component:
        component.amount += 1
        db.session.commit()
    return jsonify({}) # Function is used in static/custom.js

# Maps removeOne() function as handler for address '/components/remove-one'
# Function is used for JavaScript functions found in '/static/custom.js'
@components.route('/remove-one', methods=['POST'])
def removeOne():
    component = json.loads(request.data)
    componentId = component['componentId']
    component = Component.query.get_or_404(componentId)
    if component:
        if component.amount > 0:
            component.amount -= 1
            db.session.commit()
    return jsonify({}) # Function is used in static/custom.js
