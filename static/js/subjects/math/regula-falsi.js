const calculateRfButton = document.querySelector(".calculate-btn");

calculateRfButton.addEventListener("click", () => {
  const rfFunction = document.getElementById("function").value;
  const rfA = document.getElementById("a-value").value;
  const rfB = document.getElementById("b-value").value;
  const iterations = document.getElementById("iterations").value;

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
      if (response.ok) {
        return response.json();
      } else {
        console.error("Invalid Response");
      }
    })
    .then((data) => {
      for (let i = 0; i < data.length; i++) {
        document.querySelector(
          ".answer-text"
        ).innerHTML += `<br> Iteration ${i}, X = ${data[i][1].toFixed(
          4
        )}, f(X) = ${data[i][2].toFixed(4)} `;
      }
    });
});
