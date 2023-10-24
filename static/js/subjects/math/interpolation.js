const interpolationCalculateButton = document.querySelector(
  ".btn-calculate-inter"
);
const applyInterpolationDataPointsBtn = document.getElementById(
  "btn-inter-apply-data-points"
);
const resetBtn = document.querySelector(".btn-reset");
const calculateInterpolationBtn = document.querySelector(
  ".btn-calculate-inter"
);

let globalNumDataPts = 0;

applyInterpolationDataPointsBtn.addEventListener("click", () => {
  const numDataPts = document.getElementById("inter-num-data-points").value;
  globalNumDataPts = numDataPts;
  document.querySelector(".inter-data-points").innerHTML = "";
  if (numDataPts > 0 && numDataPts < 10) {
    for (let i = 0; i < numDataPts; i++) {
      document.querySelector(
        ".inter-data-points"
      ).innerHTML += `<br> <div class = "x${i}">
      <label for = "x${i}"> Enter X${i}: </label>
      <input type = "number" class = "x${i}-input">
      </div>
      <div class = "y${i}">
      <label for = "y${i}"> Enter Y${i}: </label>
      <input type = "number" class = "y${i}-input">
      </div>`;
    }
  } else {
    alert("Please Enter A Valid Number of data Points (Range 1-10)");
  }
});

resetBtn.addEventListener("click", () => {
  document.querySelector(".inter-data-points").innerHTML = "";
  document.getElementById("inter-num-data-points").value = "";
  document.getElementById("pt-inter").value = "";
});

calculateInterpolationBtn.addEventListener("click", () => {
  let x = [];
  let y = [];
  for (let i = 0; i < globalNumDataPts; i++) {
    x.push(document.querySelector(`.x${i}-input`).value);
    y.push([document.querySelector(`.y${i}-input`).value]);
  }
  const ptToInterpolate = document.getElementById("pt-inter").value;
  fetch("/interpolation-solver", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      x: x,
      y: y,
      ptInter: ptToInterpolate,
      numDataPts: globalNumDataPts,
    }),
  })
    .then((response) => {
      if (response.ok) {
        return response.json();
      }
    })
    .then((data) => {
      console.log(data);
    });
});
