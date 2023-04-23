
# Testing home view
def test_home(client):
    response = client.get('/')
    assert b"Navigation" in response.data

# Testing report view and making sure everything is working
def test_report(client, app, captured_templates):

    with app.app_context():
        client.get("/report")
        assert len(captured_templates) != 0
        template, context = captured_templates[0]
        assert template.name == "report.html"
        assert "components" in context
        firstCount = context["components"].count()
        
        client.post("/components/add", data={
            "name": "TEST_REPORT",
            "description": "THIS COMPONENT WAS ADDED DURING AUTOMATIC TESTING & SHOULD HAVE BEEN DELETED AUTOMATICALLY",
            "amount": 0,
            "minimumAmount": 5
        })

        client.get("/report")
        assert len(captured_templates) == 2
        template, context = captured_templates[0]
        newCount = context["components"].count()
        assert newCount == firstCount + 1

        components = context["components"].all()
        lastComponent = components[-1]
        assert lastComponent.name == "TEST_REPORT"

        client.post("/components/delete", json={
            "componentId": lastComponent.id,
        })

        response = client.get(f"components/view/{lastComponent.id}")
        assert response.status_code == 404
