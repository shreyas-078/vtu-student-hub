const applyNumPointsButton = document.querySelector("#apply-num-data-pts");
const calculateButton = document.querySelector(".calculate-btn");

let globalNumDataPts = 0;

applyNumPointsButton.addEventListener("click", () => {
  const numDataPts = document.getElementById("num-data-pts-input").value;
  globalNumDataPts = numDataPts;
  document.querySelector(".lagrange-main").classList.remove("invisible");
  document.querySelector(".data-pts").innerHTML = "";
  if (numDataPts > 0 && numDataPts < 10) {
    for (let i = 0; i < numDataPts; i++) {
      document.querySelector(
        ".data-pts"
      ).innerHTML += `<br> <div class = "x${i}">
      <label for = "x${i}"> Enter X${i}: </label>
      <input type = "number" class = "x${i}-input">
      </div>
      <div class = "y${i}">
      <label for = "y${i}"> Enter Y${i}: </label>
      <input type = "number" class = "y${i}-input">
      </div>`;
    }
    document.querySelector(".data-pts").innerHTML += `<div class = "target-x">
      <label for = "target-x-label"> Enter Point to Find Value At </label>
      <input type = "number" class = "target-x-input">`;
  } else {
    alert("Please Enter A Valid Number of data Points (Range 1-10)");
  }
});

calculateButton.addEventListener("click", () => {
  let x = [];
  let y = [];
  for (let i = 0; i < globalNumDataPts; i++) {
    x.push(document.querySelector(`.x${i}-input`).value);
    y.push(document.querySelector(`.y${i}-input`).value);
  }
  const val = document.querySelector(".target-x-input").value;
  fetch("/lagrange-calci", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      x: x,
      y: y,
      a: val,
      n: globalNumDataPts,
    }),
  })
    .then((response) => {
      if (response.ok) {
        return response.json();
      }
    })
    .then((data) => {
      document.querySelector(
        ".ans-text"
      ).textContent = `Value of Y at ${data[0]} is: ${data[1]}`;
    });
});
