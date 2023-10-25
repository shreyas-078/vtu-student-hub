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
  document.getElementById("pt-inter").value = "";
  const numDataPts = document.querySelector("#inter-num-data-points").value;
  if (numDataPts === "") {
    globalNumDataPts = 0;
  } else {
    globalNumDataPts = +numDataPts;
  }
  document.querySelector(".inter-data-points").innerHTML = "";
  if (numDataPts >= 3 && numDataPts < 10) {
    document.querySelector(".inter-data-points").classList.remove("invisible");
    for (let i = 0; i < numDataPts; i++) {
      document.querySelector(
        ".inter-data-points"
      ).innerHTML += `<br> <div class = "x${i} alignment-fix">
      <label for = "x${i}"> Enter X(${i}): </label>
      <input type = "number" class = "x-text x${i}-input">
      </div>
      <div class = "y${i} alignment-fix">
      <label for = "y${i}"> Enter Y(${i}): </label>
      <input type = "number" class = "y-text y${i}-input">
      </div>`;
    }
  } else {
    alert("Please Enter A Valid Number of data Points (Range 3-10)");
  }
});

resetBtn.addEventListener("click", () => {
  document.querySelector(".inter-data-points").innerHTML = "";
  document.getElementById("inter-num-data-points").value = "";
  document.getElementById("pt-inter").value = "";
  document.querySelector(".inter-data-points").classList.add("invisible");
  document.querySelector(".ans-text").textContent = "";
});

calculateInterpolationBtn.addEventListener("click", () => {
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
  if (document.getElementById("pt-inter").value === "") {
    alert("Please enter your data correctly");
    return;
  }
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
      ptInter: +ptToInterpolate,
      numDataPts: globalNumDataPts,
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
      alert("An error occured. Try again with different values.");
    });
});
