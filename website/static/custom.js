function deleteComponent(componentId) {
    if (confirm("Are you sure you want to delete this component?") == true) {
        fetch("/delete-component", {
            method: "POST",
            body: JSON.stringify({ componentId: componentId }),
        }).then((_res) => {
            window.location.href = "/components";
        })
    }
}

function addOne(componentId) {
    fetch("/add-one", {
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
    fetch("/remove-one", {
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