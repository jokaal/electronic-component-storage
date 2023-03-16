function addOne(componentId) {
    fetch("/add-one", {
        method: "POST",
        body: JSON.stringify({ componentId: componentId }),
    }).then((_res) => {
        divId = 'amount-' + componentId;
        amountDiv = document.getElementById(divId);
        amount = parseInt(amountDiv.innerHTML);
        amountDiv.innerHTML = amount + 1;
        // window.location.href = "/";
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