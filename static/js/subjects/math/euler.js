const calculateButton = document.getElementById("calculate-euler");

calculateButton.addEventListener("click", () => {
    const eulerFunction = document.getElementById("function");
    const eulerX0 = document.getElementById("x0");
    const eulerY0 = document.getElementById("y0");
    const eulerN = document.getElementById("n");
    const eulerH = document.getElementById("h");
    fetch("/euler", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            function: eulerFunction,
            X0: eulerX0,
            Y0: eulerY0,
            N: eulerN,
            H: eulerH,
        }),
    })
        .then((response) => {
            if (response.ok) {
                return response.json();
            }
        })
        .then((data) => {
            console.log(data);
        });
});

console.log(calculateButton);
