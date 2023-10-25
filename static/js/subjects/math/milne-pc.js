const mpcCalculateButton = document.querySelector(".btn-milne-pc-answer");
const mpcResetButton = document.querySelector(".btn-milne-pc-reset");

mpcCalculateButton.addEventListener("click", () => {
  const mpcFunction = document.querySelector("#milne-pc-function-input").value;
  const mpcX0 = document.querySelector("#milne-pc-x0-input").value;
  const mpcY0 = document.querySelector("#milne-pc-y0-input").value;
  const mpcX1 = document.querySelector("#milne-pc-x1-input").value;
  const mpcY1 = document.querySelector("#milne-pc-y1-input").value;
  const mpcX2 = document.querySelector("#milne-pc-x2-input").value;
  const mpcY2 = document.querySelector("#milne-pc-y2-input").value;
  const mpcX3 = document.querySelector("#milne-pc-x3-input").value;
  const mpcY3 = document.querySelector("#milne-pc-y3-input").value;

  if (
    !mpcFunction ||
    !mpcX0 ||
    !mpcY0 ||
    !mpcX1 ||
    !mpcY1 ||
    !mpcX2 ||
    !mpcY2 ||
    !mpcX3 ||
    !mpcY3
  ) {
    alert("Please enter all values before calculating");
    return;
  }

  fetch("/milne-pc", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      f: mpcFunction,
      x0: mpcX0,
      y0: mpcY0,
      x1: mpcX1,
      y1: mpcY1,
      x2: mpcX2,
      y2: mpcY2,
      x3: mpcX3,
      y3: mpcY3,
    }),
  })
    .then((response) => {
      if (response.status === 500) {
        throw new Error("An Error occured. Try again with different values");
      }
      if (response.ok) {
        return response.json();
      }
    })
    .then((data) => {
      const answerDiv = document.querySelector("#milne-pc-answer");
      answerDiv.querySelector("#milne-pc-y4p").textContent =
        "Y(4) Predicted = " + data[0].toFixed(4);
      answerDiv.querySelector("#milne-pc-y4c-1").textContent =
        "Y(4) Corrected Iteration 1 = " + data[1].toFixed(4);
      answerDiv.querySelector("#milne-pc-y4c-2").textContent =
        "Y(4) Corrected Iteration 2 = " + data[2].toFixed(4);
      answerDiv.querySelector("#milne-pc-y4c-3").textContent =
        "Y(4) Corrected Iteration 3 = " + data[3].toFixed(4);
    })
    .catch((error) => {
      alert("An error occured. Try again with different values.");
    });
});

mpcResetButton.addEventListener("click", () => {
  document.querySelector("#milne-pc-function-input").value = "";
  document.querySelector("#milne-pc-x0-input").value = "";
  document.querySelector("#milne-pc-y0-input").value = "";
  document.querySelector("#milne-pc-x1-input").value = "";
  document.querySelector("#milne-pc-y1-input").value = "";
  document.querySelector("#milne-pc-x2-input").value = "";
  document.querySelector("#milne-pc-y2-input").value = "";
  document.querySelector("#milne-pc-x3-input").value = "";
  document.querySelector("#milne-pc-y3-input").value = "";
});
