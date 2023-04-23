
# Basic tests for components
def test_component_crud(client, app, captured_templates):
    with app.app_context():

        # GET ALL COMPONENTS AND REMEMBER TOTAL COUNT
        client.get("/components/")
        assert len(captured_templates) != 0
        template, context = captured_templates[0]
        assert template.name == "components/components.html"
        assert "pagination" in context
        firstCount = context["pagination"].total

        # ADD NEW COMPONENT
        client.post("/components/add", data={
            "name": "TEST_COMPONENT",
            "description": "THIS COMPONENT WAS ADDED DURING AUTOMATIC TESTING & SHOULD HAVE BEEN DELETED AUTOMATICALLY",
            "amount": 0
        })

        # GET ALL COMPONENTS AND CHECK THAT COUNT HAS INCREASED
        client.get("/components/")
        assert len(captured_templates) == 2
        template, context = captured_templates[1]
        newCount = context["pagination"].total
        assert newCount == firstCount + 1

        # GET LAST COMPONENT IN LIST AND CHECK VIEW
        component = context["pagination"].items[newCount - 1]
        assert component.name == "TEST_COMPONENT"
        client.get(f"/components/view/{component.id}")
        assert len(captured_templates) == 3
        template, context = captured_templates[2]
        assert context["component"].name == "TEST_COMPONENT"
        assert template.name == "components/functions/view_component.html"

        # TEST COMPONENT AMOUNT CHANGING FUNCTIONS
        for i in range(2):
            client.post("/components/add-one", json={
                "componentId": component.id,
            })
        client.post("/components/remove-one", json={
                "componentId": component.id,
        })
        client.get(f"/components/view/{component.id}")
        assert len(captured_templates) == 4
        template, context = captured_templates[3]
        assert context["component"].amount == 1

        # TEST COMPONENT EDITING
        client.post(f"/components/edit/{component.id}", data={
            "name": "TEST_COMPONENT_EDITED",
            "amount": 10
        })
        client.get(f"/components/view/{component.id}")
        assert len(captured_templates) == 5
        template, context = captured_templates[4]
        assert context["component"].name == "TEST_COMPONENT_EDITED"
        assert context["component"].amount == 10

        # DELETE COMPONENT AND CHECK THAT COUNT IS EQUAL TO FIRST COUNT
        client.post("/components/delete", json={
            "componentId": component.id,
        })
        client.get("/components/")
        assert len(captured_templates) == 6
        template, context = captured_templates[5]
        count = context["pagination"].total    
        assert count == firstCount
