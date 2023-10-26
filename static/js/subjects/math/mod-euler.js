const calculateButton = document.getElementById("calculate-mod-euler");
const resetButton = document.getElementById("final-ans");

calculateButton.addEventListener("click", () => {
  const eulerFunction = document.getElementById("function").value;
  const eulerX0 = document.getElementById("x0").value;
  const eulerY0 = document.getElementById("y0").value;
  const eulerN = document.getElementById("n").value;
  const eulerH = document.getElementById("h").value;
  if (!eulerFunction || !eulerX0 || !eulerY0 || !eulerN || !eulerH) {
    alert("Please enter all values before calculating");
    return;
  }
  if (eulerN <= 0 || eulerH <= 0) {
    alert("Iterations or Step Length cannot be 0 or negative");
  }
  fetch("/mod-euler", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      F: eulerFunction,
      X0: eulerX0,
      Y0: eulerY0,
      N: eulerN,
      H: eulerH,
    }),
  })
    .then((response) => {
      if (response.status === 500) {
        throw new Error("Try again");
      }
      if (response.ok) {
        return response.json();
      }
    })
    .then((data) => {
      const ansPara = document.getElementById("final-ans");
      ansPara.innerHTML = `Initial Guess of Y at ${data[0][0]} = ${data[0][1]} <br>`;
      ansPara.innerHTML += `Iterations:`;
      console.log(data);
      for (let i = 0; i < data[1].length; i++) {
        ansPara.innerHTML += ` <br> ${i + 1}: ${data[1][i].toFixed(4)}`;
      }
      ansPara.innerHTML += `<br> Final Value: <br>
            ${data[data.length - 1]}`;
    })
    .catch((error) => {
      alert("An Error Occured. Try again with different values.");
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
