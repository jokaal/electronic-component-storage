from flask import Blueprint, render_template
from ..database.models import Component
from .. import db

# Creating Blueprint, URL prefix is '/'
views = Blueprint('views', __name__)

# Mapping home() function as handler for address '/'
# Used to render home page
# Renders ./templates/home.html template
@views.route('/')
def home():
    return render_template('home.html')

# Mapping report() function as handler for address '/report'
# Used to render report page
# Renders ./templates/report.html template
@views.route('/report')
def report():
    query = Component.query.filter(Component.amount <= Component.minimum_amount)
    return render_template('report.html', components=query)