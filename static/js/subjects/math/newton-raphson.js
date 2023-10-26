const calculateButton = document.querySelector(".calculate-btn");
const resetButton = document.querySelector(".reset-btn");

calculateButton.addEventListener("click", () => {
  const nrFunction = document.getElementById("function").value;
  const initApproximation = document.getElementById(
    "initial-approximation"
  ).value;
  const iterations = document.getElementById("iterations").value;

  if (!iterations || !nrFunction || !initApproximation) {
    alert("Please enter all values before calculating.");
    return;
  }

  if (iterations <= 0) {
    alert("Number of iterations cannot be negative or zero");
  }

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
      if (response.status === 500) {
        throw new Error("Try again");
      }
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
    })
    .catch((error) => {
      alert("An Error occured. Try again with different values.");
    });
});

resetButton.addEventListener("click", () => {
  document.getElementById("function").value = "";
  document.getElementById("initial-approximation").value = "";
  document.getElementById("iterations").value = "";
  document.querySelector("#answer-text").innerHTML = "";
});
