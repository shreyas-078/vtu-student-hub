const calculateButton = document.getElementById("calculate-euler");

calculateButton.addEventListener("click", () => {
    const eulerFunction = document.getElementById("function").value;
    const eulerX0 = document.getElementById("x0").value;
    const eulerY0 = document.getElementById("y0").value;
    const eulerN = document.getElementById("n").value;
    const eulerH = document.getElementById("h").value;
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
            const ansPara = document.getElementById("final-ans");
            for (let i = 0; i < eulerN + 1; i++) {
                ansPara.innerHTML +=
                    "<br>" + `Y at + ${data[i][0]} = ${data[i][1]}`;
            }
        });
});
