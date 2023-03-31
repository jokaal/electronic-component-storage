function deleteComponent(componentId) {
    if (confirm("Are you sure you want to delete this component?") == true) {
        fetch("/components/delete", {
            method: "POST",
            body: JSON.stringify({ componentId: componentId }),
        }).then((_res) => {
            window.location.href = "/components";
        })
    }
}

function addOne(componentId) {
    fetch("/components/add-one", {
        method: "POST",
        body: JSON.stringify({ componentId: componentId }),
    }).then((_res) => {
        divId = 'amount-' + componentId;
        amountDiv = document.getElementById(divId);
        amount = parseInt(amountDiv.innerHTML);
        amountDiv.innerHTML = amount + 1;
    })
}

function removeOne(componentId) {
    fetch("/components/remove-one", {
        method: "POST",
        body: JSON.stringify({ componentId: componentId }),
    }).then((_res) => {
        divId = 'amount-' + componentId;
        amountDiv = document.getElementById(divId);
        amount = parseInt(amountDiv.innerHTML);
        if (amount > 0) {
            amountDiv.innerHTML = amount - 1;
        }
    })
}

function deleteProject(projectId) {
    if (confirm("Are you sure you want to delete this project?") == true) {
        fetch("/projects/delete", {
            method: "POST",
            body: JSON.stringify({ projectId: projectId }),
        }).then((_res) => {
            window.location.href = "/projects";
        })
    }
}

function addComponentToProject(projectId) {
    fetch("/projects/add-component-to-project", {
        method: "POST",
        body: JSON.stringify({ projectId: projectId }),
    }).then((_res) => {
        window.location.href = "/projects/view/" + projectId;
    })
}