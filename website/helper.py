from flask import flash
import re, sys, math
from .database.models import Project, ProjectComponent, Component
from . import db, config

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

def projectErrors(project):
    errors = False
    messages = []

    if not project.name: # HTML form already checks this
        messages.append('Project must have a name!')
        errors = True

    if messages:
        flash(' '.join(messages), category='error')

    return errors

def findMax(projectComponents):
    buildMax = sys.maxsize
    for projectComponent in projectComponents:
        amountNeeded = projectComponent.amount
        if not projectComponent.component:
            return 0
        amountStored = projectComponent.component.amount
        if amountNeeded > amountStored:
            return 0
        else:
            if amountNeeded != 0:
                canBuild = math.floor(amountStored / amountNeeded)
                buildMax = canBuild if canBuild < buildMax else buildMax
    return buildMax

def allowedFile(fileName, allowed):
    return '.' in fileName and \
           fileName.rsplit('.', 1)[1].lower() in allowed