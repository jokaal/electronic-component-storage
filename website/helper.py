from flask import flash
import re, sys, math
from .database.models import Project, ProjectComponent, Component
from . import db, config

# A helper function to help validate components coming from a request
# Component must have a name & the URL must be valid or None
# If there are errors then they are flashed using Flasks in-built flash system
# Returns false if there are no errors, true if there are
def componentErrors(component: Component) -> bool:
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

# A helper function to help validate projects coming from a request
# Component must have a name
# If there are errors then they are flashed using Flasks in-built flash system
# Returns False if there are no errors, True if there are
def projectErrors(project: Project) -> bool:
    errors = False
    messages = []

    if not project.name: # HTML form already checks this
        messages.append('Project must have a name!')
        errors = True

    if messages:
        flash(' '.join(messages), category='error')

    return errors

# A helper function to help find the maximum build amount for a project
# Iterates and checks every ProjectComponent to see if Component is set
# If Component is set then checks how many are needed to build and how many are in storage
# Returns the calculated integer for maximum build amount
def findMax(projectComponents: list[ProjectComponent]) -> int:
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

# A helper function used to check if file type is allowed
# Uses the file name and a dictionary of allowed extensions i.e. {'json'}
# Returns True if allowed, otherwise False
def allowedFile(fileName: str, allowed: dict[str]) -> bool:
    return '.' in fileName and \
           fileName.rsplit('.', 1)[1].lower() in allowed