from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from .models import Component, Project
from . import db
import json
import re

views = Blueprint('views', __name__)

# HOME

@views.route('/')
def home():
    return render_template('home.html')

# COMPONENT FUNCTIONS

@views.route('/components', methods=['GET', 'POST'])
def components():
    search = None if request.args.get('search') == '' else request.args.get('search')
    if search:
        # https://stackoverflow.com/questions/4926757/sqlalchemy-query-where-a-column-contains-a-substring
        if '*' in search or '_' in search:
            looking_for = search.replace('_', '__').replace('*', '%').replace('?', '_')
        else:
            looking_for = '%{0}%'.format(search)

        query = Component.query.filter((Component.name.ilike(looking_for)) | (Component.value.ilike(looking_for)) | (Component.description.ilike(looking_for)))

        return render_template('components/components.html', components=query, search=request.args.get('search'))
    return render_template('components/components.html', components=Component.query.all())

@views.route('/add-component', methods=['GET', 'POST'])
def add_component():
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
            return redirect(url_for('views.components'))
        else:
            return render_template('components/functions/add_component.html', component=new_component)

    return render_template('components/functions/add_component.html')

def componentErrors(component):
    errors = False
    messages = []

    if not component.name: # HTML form already checks this
        messages.append('Component must have a name!')
        errors = True

    if component.amount and int(component.amount) < 0: # HTML form already checks this
        messages.append('Component amount can\'t be less than 0!')
        errors = True

    if component.url:
        # https://stackoverflow.com/questions/7160737/how-to-validate-a-url-in-python-malformed-or-not
        regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        if re.match(regex, component.url) is None:
            messages.append('Please enter a valid URL address!')
            errors = True

    if messages:
        flash(' '.join(messages), category='error')

    return errors

@views.route('/component/<id>')
def view_component(id):
    if 'edit-component' not in request.referrer: # Allows going back to search result but after editing search is lost
        return render_template('components/functions/view_component.html', component=Component.query.get(id), referrer=request.referrer)
    return render_template('components/functions/view_component.html', component=Component.query.get(id))

@views.route('/edit-component/<id>', methods=['GET', 'POST'])
def edit_component(id):
    component = Component.query.get(id)

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
            return redirect(url_for('views.view_component', id=id))

    return render_template('components/functions/edit_component.html', component=component, referrer=request.referrer)

@views.route('/delete-component', methods=['POST'])
def delete_component():
    component = json.loads(request.data)
    componentId = component['componentId']
    component = Component.query.get(componentId)
    if component:
        db.session.delete(component)
        db.session.commit()
    return jsonify({}) # Function is used in static/custom.js

@views.route('/add-one', methods=['POST'])
def add_one():
    component = json.loads(request.data)
    componentId = component['componentId']
    component = Component.query.get(componentId)
    if component:
        component.amount += 1
        db.session.commit()
    return jsonify({}) # Function is used in static/custom.js

@views.route('/remove-one', methods=['POST'])
def remove_one():
    component = json.loads(request.data)
    componentId = component['componentId']
    component = Component.query.get(componentId)
    if component:
        if component.amount > 0:
            component.amount -= 1
            db.session.commit()
    return jsonify({}) # Function is used in static/custom.js


# PROJECT FUNCTIONS

@views.route('/projects', methods=['GET', 'POST'])
def projects():
    search = None if request.args.get('search') == '' else request.args.get('search')
    if search:
        # https://stackoverflow.com/questions/4926757/sqlalchemy-query-where-a-column-contains-a-substring
        if '*' in search or '_' in search:
            looking_for = search.replace('_', '__').replace('*', '%').replace('?', '_')
        else:
            looking_for = '%{0}%'.format(search)

        query = Project.query.filter((Project.name.ilike(looking_for)))

        return render_template('projects/projects.html', projects=query, search=request.args.get('search'))
    return render_template('projects/projects.html', projects=Project.query.all())

@views.route('/create-project', methods=['GET', 'POST'])
def create_project():
    if request.method == 'POST':
        name = None if request.form.get('name') == '' else request.form.get('name') # Form return an empty string if not filled but we need null for database
        new_project = Project(name=name)
        
        if not projectErrors(new_project):
            db.session.add(new_project)
            db.session.commit()
            flash(f'Project \'{name}\' has been created!', category='success')
            return redirect(url_for('views.view_project', id=new_project.id))
        else:
            return render_template('projects/functions/create_project.html', project=new_project)

    return render_template('projects/functions/create_project.html')

def projectErrors(project):
    errors = False
    messages = []

    if not project.name: # HTML form already checks this
        messages.append('Project must have a name!')
        errors = True

    if messages:
        flash(' '.join(messages), category='error')

    return errors

@views.route('/project/<id>')
def view_project(id):
    if 'edit-project' and 'create-project' not in request.referrer: # Allows going back to search result but after editing search is lost
        return render_template('projects/functions/view_project.html', project=Project.query.get(id), referrer=request.referrer)
    return render_template('projects/functions/view_project.html', project=Project.query.get(id))
