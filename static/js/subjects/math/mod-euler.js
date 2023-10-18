const calculateButton = document.getElementById("calculate-mod-euler");

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
            ansPara.innerHTML = `Initial Guess of Y at ${data[0][0]} = ${data[0][1]} <br>`;
            ansPara.innerHTML += `Iterations:`;
            for (let i = 1; i < data.length - 1; i++) {
                ansPara.innerHTML += ` <br> ${i}: ${data[i]}`;
            }
            ansPara.innerHTML += `<br> Final Value: <br>
            ${data[data.length - 1]}`;
        });
});
