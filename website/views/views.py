from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from ..database.models import Component, ProjectComponent
from .. import db, config

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template('home.html')

@views.route('/report')
def report():

    query = Component.query.filter(Component.amount <= Component.minimum_amount)

    return render_template('report.html', components=query)