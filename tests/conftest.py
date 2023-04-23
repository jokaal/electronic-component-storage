import pytest
from website import create_app
from flask import template_rendered

# https://flask.palletsprojects.com/en/2.2.x/testing/
# Used to create application instance for testing
@pytest.fixture()
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
    })

    # other setup can go here

    yield app

    # clean up / reset resources here

# Set up for testing client
@pytest.fixture()
def client(app):
    return app.test_client()

# https://stackoverflow.com/questions/23987564/test-flask-render-template-context/24914680#24914680
# Set up for catching templates and their context
@pytest.fixture
def captured_templates(app):
    recorded = []

    def record(sender, template, context, **extra):
        recorded.append((template, context))

    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)