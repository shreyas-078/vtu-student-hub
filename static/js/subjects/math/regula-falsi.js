const calculateRfButton = document.querySelector(".calculate-btn");
const resetButton = document.querySelector(".reset-btn");

calculateRfButton.addEventListener("click", () => {
  const rfFunction = document.getElementById("function").value;
  const rfA = document.getElementById("a-value").value;
  const rfB = document.getElementById("b-value").value;
  const iterations = document.getElementById("iterations").value;

  if (!rfFunction || !rfA || !rfB || !iterations) {
    alert("Please enter all values before calculating.");
    return;
  }

  if (iterations <= 0) {
    alert("Number of iterations cannot be 0 or negative");
    return;
  }

  fetch("/regula-falsi-calci", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      rfFunction: rfFunction,
      rfA: rfA,
      rfB: rfB,
      iterations: iterations,
    }),
  })
    .then((response) => {
      if (response.status === 500) {
        throw new Error("Try again.");
      }
      if (response.ok) {
        return response.json();
      } else {
        console.error("Invalid Response");
      }
    })
    .then((data) => {
      for (let i = 0; i < data.length; i++) {
        document.querySelector(".answer-text").innerHTML += `<br> Iteration ${
          i + 1
        }: X = ${data[i][1].toFixed(4)}, f(X) = ${data[i][2].toFixed(4)} `;
      }
    })
    .catch((error) => {
      alert("An Error Occured. Try again with different values.");
    });
});

resetButton.addEventListener("click", () => {
  document.getElementById("function").value = "";
  document.getElementById("a-value").value = "";
  document.getElementById("b-value").value = "";
  document.getElementById("iterations").value = "";
  document.querySelector(".answer-text").innerHTML = "";
});
