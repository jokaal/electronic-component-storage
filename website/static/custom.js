function deleteComponent(componentId) {
    if (confirm("Are you sure you want to delete this component?\nThe component is also removed from any project that uses it.") == true) {
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
    fetch("/projects/project-component/add", {
        method: "POST",
        body: JSON.stringify({ projectId: projectId }),
    }).then((_res) => {
        window.location.href = "/projects/view/" + projectId;
    })
}

function chooseComponentForProject(projectComponentId, componentId, projectId) {
    fetch("/projects/project-component/add-component", {
        method: "POST",
        body: JSON.stringify({ projectComponentId: projectComponentId, componentId: componentId }),
    }).then((_res) => {
        window.location.href = "/projects/view/" + projectId;
    })
}

function editProjectComponentAmount(projectComponentId, projectId) {
    var answer = prompt("Enter a number: "); // https://stackoverflow.com/questions/46552085/javascript-force-specific-data-type-input-or-accept-only-digits-in-input
    if (answer == null) return;
    while (!/^0*?[0-9]\d*$/.test(answer)) { // Accepts all positive numbers above 0. Accepts numbers with leading zeroes e.g.: 0123, 00123.
        alert("You did not enter a valid number.");
        answer = prompt("Enter a number: ");
        if (answer == null) return;
    }
    fetch("/projects/project-component/amount", {
        method: "POST",
        body: JSON.stringify({ projectComponentId: projectComponentId, amount: answer }),
    }).then((_res) => {
        window.location.href = "/projects/view/" + projectId;
    })
}

function editProjectComponentComment(projectComponentId, projectId) {
    var answer = prompt("Add a new comment (leave empty to delete): ");
    if (answer == null) return;
    fetch("/projects/project-component/comment", {
        method: "POST",
        body: JSON.stringify({ projectComponentId: projectComponentId, comment: answer }),
    }).then((_res) => {
        window.location.href = "/projects/view/" + projectId;
    })
}

function deleteProjectComponent(projectComponentId, projectId) {
    if (confirm("Are you sure you want to delete this project component?") == true) {
        fetch("/projects/project-component/delete", {
            method: "POST",
            body: JSON.stringify({ projectComponentId: projectComponentId }),
        }).then((_res) => {
            window.location.href = "/projects/view/" + projectId;
        })
    }
}

function endBuild(projectId) {
    if (confirm("Are you sure you want to end this build?\nThis will NOT reduce the components amounts in storage.") == true) {
        fetch("/projects/build/end", {
            method: "POST",
            body: JSON.stringify({ projectId: projectId }),
        }).then((_res) => {
            window.location.href = "/projects/view/" + projectId;
        })
    }
}