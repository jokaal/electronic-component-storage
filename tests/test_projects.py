
# Basic tests for projects
def test_project_crud(client, app, captured_templates):
    with app.app_context():

        # GET ALL PROJECTS AND REMEMBER TOTAL COUNT
        client.get("/projects/")
        assert len(captured_templates) != 0
        template, context = captured_templates[0]
        assert template.name == "projects/projects.html"
        assert "pagination" in context
        firstCount = context["pagination"].total

        # ADD NEW PROJECT
        client.post("/projects/create", data={
            "name": "TEST_PROJECT"
        })

        # GET ALL PROJECTS AND CHECK THAT COUNT HAS INCREASED
        client.get("/projects/")
        assert len(captured_templates) == 2
        template, context = captured_templates[1]
        newCount = context["pagination"].total
        assert newCount == firstCount + 1

        # GET LAST PROJECT IN LIST AND CHECK VIEW
        project = context["pagination"].items[newCount - 1]
        assert project.name == "TEST_PROJECT"
        client.get(f"/projects/view/{project.id}")
        assert len(captured_templates) == 3
        template, context = captured_templates[2]
        assert context["project"].name == "TEST_PROJECT"
        assert template.name == "projects/functions/view_project.html"

        # TEST PROJECT EDITING
        client.post(f"/projects/edit/{project.id}", data={
            "name": "TEST_PROJECT_EDITED"
        })
        client.get(f"/projects/view/{project.id}")
        assert len(captured_templates) == 4
        template, context = captured_templates[3]
        assert context["project"].name == "TEST_PROJECT_EDITED"

        # DELETE PROJECT AND CHECK THAT COUNT IS EQUAL TO FIRST COUNT
        client.post("/projects/delete", json={
            "projectId": project.id,
        })
        client.get("/projects/")
        assert len(captured_templates) == 5
        template, context = captured_templates[4]
        count = context["pagination"].total    
        assert count == firstCount
