const chooseButton = document.querySelector(".choice-btn");
const interpolationCalculateButton = document.querySelector(
  ".btn-calculate-inter"
);
const applyInterpolationDataPointsBtn = document.getElementById(
  "btn-inter-apply-data-points"
);
const applyExtrapolationPointsBtn = document.getElementById(
  "btn-extra-apply-data-points"
);
const resetBtn = document.querySelector(".btn-reset");
const calculateInterpolationBtn = document.querySelector(
  ".btn-calculate-inter"
);

chooseButton.addEventListener("click", () => {
  const selection = document.querySelector(".ip-ep-select");
  if (selection.value === "") {
    alert("Select a Valid Option");
    return;
  }
  if (selection.value === "inter") {
    document.querySelector(".extrapolation").classList.add("invisible");
    document.querySelector(".interpolation").classList.remove("invisible");
  } else {
    document.querySelector(".extrapolation").classList.remove("invisible");
    document.querySelector(".interpolation").classList.add("invisible");
  }
});

applyInterpolationDataPointsBtn.addEventListener("click", () => {
  const numDataPts = document.getElementById("inter-num-data-points").value;
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
      <input type = "number" class = "Y${i}-input">
      </div>`;
    }
  } else {
    alert("Please Enter A Valid Number of data Points (Range 1-10)");
  }
});

applyExtrapolationPointsBtn.addEventListener("click", () => {
  const numDataPts = document.getElementById("extra-num-data-points").value;
  document.querySelector(".extra-data-points").innerHTML = "";
  if (numDataPts > 0 && numDataPts < 10) {
    for (let i = 0; i < numDataPts; i++) {
      document.querySelector(
        ".extra-data-points"
      ).innerHTML += `<br> <div class = "x${i}">
      <label for = "x${i}"> Enter X${i}: </label>
      <input type = "number" class = "x${i}-input">
      </div>
      <div class = "y${i}">
      <label for = "y${i}"> Enter Y${i}: </label>
      <input type = "number" class = "Y${i}-input">
      </div>`;
    }
  } else {
    alert("Please Enter A Valid Number of data Points (Range 1-10)");
  }
});

resetBtn.addEventListener("click", () => {
  document.querySelector(".extrapolation").classList.add("invisible");
  document.querySelector(".interpolation").classList.add("invisible");
  document.querySelector(".extra-data-points").innerHTML = "";
  document.querySelector(".inter-data-points").innerHTML = "";
  document.querySelector(".ip-ep-select").value = "";
  document.getElementById("inter-num-data-points").value = "";
  document.getElementById("extra-num-data-points").value = "";
});

calculateInterpolationBtn.addEventListener("click", () => {});
