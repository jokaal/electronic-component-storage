from flask import Blueprint, render_template, request, flash, jsonify
from .models import Component
from . import db
import json

views = Blueprint('views', __name__)

@views.route("/", methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        name = request.form.get('name')
        amount = request.form.get('amount')

        new_component = Component(name=name, amount=amount)
        db.session.add(new_component)
        db.session.commit()

        flash('Component added!', category='success')

    return render_template("home.html", components=Component.query.all())

@views.route('add-one', methods=['POST'])
def add_one():
    component = json.loads(request.data)
    componentId = component['componentId']
    component = Component.query.get(componentId)
    if component:
        component.amount += 1
        db.session.commit()
    return jsonify({})

@views.route('remove-one', methods=['POST'])
def remove_one():
    component = json.loads(request.data)
    componentId = component['componentId']
    component = Component.query.get(componentId)
    if component:
        if component.amount > 0:
            component.amount -= 1
            db.session.commit()
    return jsonify({})


@views.route("/about/")
def about():
    return render_template("about.html")


@views.route("/contact/")
def contact():
    return render_template("contact.html")
