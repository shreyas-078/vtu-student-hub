const calculateButton = document.querySelector(".calculate-btn");

calculateButton.addEventListener("click", () => {
  const nrFunction = document.getElementById("function").value;
  const initApproximation = document.getElementById(
    "initial-approximation"
  ).value;
  const iterations = document.getElementById("iterations").value;
  fetch("/newton-raphson-calci", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      nrFunction: nrFunction,
      initApproximation: initApproximation,
      iterations: iterations,
    }),
  })
    .then((response) => {
      if (response.ok) {
        return response.json();
      } else {
        console.error("Invalid Response");
      }
    })
    .then((data) => {
      for (let i = 0; i < data.length; i++) {
        document.getElementById("answer-text").innerHTML += `<br> Iteration: ${
          i + 1
        }, Value of X ${data[i][1]}, F(X) = ${data[i][2]} <br>`;
      }
    });
});
