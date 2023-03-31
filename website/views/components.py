from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from ..database.models import Component
from .. import db, config
from ..helper import componentErrors, projectErrors, findMax
import json

components = Blueprint('components', __name__)
per_page = config['settings']['resultsPerPage']

# COMPONENT VIEWS

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

@components.route('/add', methods=['GET', 'POST'])
def add():
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

    return render_template('components/functions/add_component.html')

@components.route('/view/<id>')
def view(id):
    referrer = None
    if 'edit' not in request.referrer: # Allows going back to search result but after editing search is lost
        referrer=request.referrer
    return render_template('components/functions/view_component.html', component=Component.query.get(id), referrer=referrer)

@components.route('/edit/<id>', methods=['GET', 'POST'])
def edit(id):
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
            return redirect(url_for('components.view', id=id))

    return render_template('components/functions/edit_component.html', component=component, referrer=request.referrer)

@components.route('/delete', methods=['POST'])
def delete():
    component = json.loads(request.data)
    componentId = component['componentId']
    component = Component.query.get(componentId)
    if component:
        db.session.delete(component)
        db.session.commit()
    return jsonify({}) # Function is used in static/custom.js

@components.route('/add-one', methods=['POST'])
def add_one():
    component = json.loads(request.data)
    componentId = component['componentId']
    component = Component.query.get(componentId)
    if component:
        component.amount += 1
        db.session.commit()
    return jsonify({}) # Function is used in static/custom.js

@components.route('/remove-one', methods=['POST'])
def remove_one():
    component = json.loads(request.data)
    componentId = component['componentId']
    component = Component.query.get(componentId)
    if component:
        if component.amount > 0:
            component.amount -= 1
            db.session.commit()
    return jsonify({}) # Function is used in static/custom.js
