const calculateButton = document.getElementById("calculate-euler");
const resetButton = document.getElementById("reset-euler");

calculateButton.addEventListener("click", () => {
  const eulerFunction = document.getElementById("function").value;
  const eulerX0 = document.getElementById("x0").value;
  const eulerY0 = document.getElementById("y0").value;
  const eulerN = document.getElementById("n").value;
  const eulerH = document.getElementById("h").value;
  if (!eulerFunction || !eulerX0 || !eulerH || !eulerN || !eulerY0) {
    alert("Please enter all the values and try again.");
    return;
  }
  if (eulerX0 >= 1000 || eulerY0 >= 1000 || eulerH >= 100 || eulerN > 6) {
    alert("Value too large. Try again.");
    return;
  }
  if (eulerN < 1 || eulerH < 0.1) {
    alert("Cannot take negative step length or negative number of iterations");
    return;
  }
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
      if (response.status === 400) {
        throw new Error(
          "Function Error, Please Enter Correct function and try again."
        );
      }
      if (response.ok) {
        if (response.status === 500) {
          throw new Error("An Error Occured. Try Different Values");
        }
        return response.json();
      }
    })
    .then((data) => {
      const ansPara = document.getElementById("final-ans");
      for (let i = 0; i < eulerN; i++) {
        ansPara.innerHTML += "<br>" + `Y(${data[i][0]}) = ${data[i][1]}`;
      }
    })
    .catch((error) => {
      alert(
        "Enter Correct Function and try again/ Values too large to compute"
      );
    });
});

resetButton.addEventListener("click", () => {
  document.getElementById("function").value = "";
  document.getElementById("x0").value = "";
  document.getElementById("y0").value = "";
  document.getElementById("n").value = "";
  document.getElementById("h").value = "";
  document.querySelector("#final-ans").innerHTML = "";
});
