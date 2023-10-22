const calculateButton = document.getElementById("calculate-mod-euler");

calculateButton.addEventListener("click", () => {
  const eulerFunction = document.getElementById("function").value;
  const eulerX0 = document.getElementById("x0").value;
  const eulerY0 = document.getElementById("y0").value;
  const eulerN = document.getElementById("n").value;
  const eulerH = document.getElementById("h").value;
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
    });
});
