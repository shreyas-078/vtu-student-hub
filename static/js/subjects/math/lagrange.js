const applyNumPointsButton = document.querySelector("#apply-num-data-pts");
const calculateButton = document.querySelector(".calculate-btn");
const resetButton = document.querySelector(".reset-btn");

let globalNumDataPts = 0;

applyNumPointsButton.addEventListener("click", () => {
  document.querySelector(".target-x-input").value = "";
  const numDataPts = document.getElementById("num-data-pts-input").value;
  globalNumDataPts = numDataPts;
  document.querySelector(".data-pts").innerHTML = "";
  if (numDataPts >= 3 && numDataPts < 10) {
    document.querySelector(".lagrange-main").classList.remove("invisible");
    for (let i = 0; i < numDataPts; i++) {
      if (i === 0) {
        document.querySelector(
          ".data-pts"
        ).innerHTML += `<div class = "x${i} alignment-fix">
      <label for = "x${i}"> Enter X(${i}): </label>
      <input type = "number" class = "x-text x${i}-input">
      </div>
      <div class = "y${i} alignment-fix">
      <label for = "y${i}"> Enter Y(${i}): </label>
      <input type = "number" class = "y-text y${i}-input">
      </div>`;
      } else {
        document.querySelector(
          ".data-pts"
        ).innerHTML += `<br> <div class = "x${i} alignment-fix">
      <label for = "x${i}"> Enter X(${i}): </label>
      <input type = "number" class = "x-text x${i}-input">
      </div>
      <div class = "y${i} alignment-fix">
      <label for = "y${i}"> Enter Y(${i}): </label>
      <input type = "number" class = "y-text y${i}-input">
      </div>`;
      }
    }
  } else {
    alert("Please Enter A Valid Number of data Points (Range 3-10)");
    return;
  }
});

calculateButton.addEventListener("click", () => {
  if (globalNumDataPts === 0) {
    alert("Please enter your data correctly");
    return;
  } else if (globalNumDataPts > 0) {
    for (let i = 0; i < globalNumDataPts; i++) {
      if (
        document.querySelector(`.x${i}-input`).value === "" ||
        document.querySelector(`.y${i}-input`).value === ""
      ) {
        alert("Please enter your data correctly");
        return;
      }
    }
  }
  if (document.querySelector(".target-x-input").value === "") {
    alert("Please enter your data correctly");
    return;
  }
  console.log(document.querySelector(".target-x-input").value === "");
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
      if (response.status === 500) {
        throw new Error("An Error Occured. You can try using different values");
      }
      if (response.ok) {
        return response.json();
      }
    })
    .then((data) => {
      document.querySelector(
        ".ans-text"
      ).textContent = `Y(${data[0]}) = ${data[1]}`;
    })
    .catch((error) => {
      alert("An Error Occured, Try Using different values.");
    });
});

resetButton.addEventListener("click", () => {
  document.querySelector(".data-pts").innerHTML = "";
  document.querySelector("#num-data-pts-input").value = "";
  document.querySelector(".target-x-input").value = "";
  document.querySelector(".lagrange-main").classList.add("invisible");
});
