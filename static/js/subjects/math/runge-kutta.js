const rkCalculateButton = document.querySelector(".btn-rk-answer");
const answerBox = document.getElementById("rk-answer");

rkCalculateButton.addEventListener("click", () => {
    const rkX0Value = document.getElementById("rk-x0-input").value;
    const rkFunction = document.getElementById("rk-function-input").value;
    const rkY0Value = document.getElementById("rk-y0-input").value;
    const rkHValue = document.getElementById("rk-h-input").value;
    const rkHelperText = answerBox.querySelector("#rk-helper-text");

    if (!rkX0Value || !rkHValue || !rkY0Value || !rkFunction) {
        rkHelperText.textContent = "Please Enter Proper Values";
        rkHelperText.classList.remove("invisible");
        return;
    }

    fetch("/runge-kutta", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            x0: rkX0Value,
            f: rkFunction,
            y0: rkY0Value,
            h: rkHValue,
        }),
    }).then((response) => {
        if (response.ok) {
            rkHelperText.classList.add("invisible");
            return response.json().then((data) => {
                const [k1, k2, k3, k4, x1, y1] = data;
                answerBox.querySelector("#rk-k1").textContent =
                    "K1 = " + k1.toFixed(4);
                answerBox.querySelector("#rk-k2").textContent =
                    "K2 = " + k2.toFixed(4);
                answerBox.querySelector("#rk-k3").textContent =
                    "K3 = " + k3.toFixed(4);
                answerBox.querySelector("#rk-k4").textContent =
                    "K4 = " + k4.toFixed(4);
                answerBox.querySelector("#rk-x1").textContent =
                    "X1 = " + x1.toFixed(4);
                answerBox.querySelector("#rk-y1").textContent =
                    "Y1 = " + y1.toFixed(4);
            });
        } else {
            console.error("Error:", response.status, response.statusText);
        }
    });
});
