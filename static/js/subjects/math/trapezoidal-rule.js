const calculateButton = document.querySelector(".calculate-btn");
const resetButton = document.querySelector(".reset-btn");

calculateButton.addEventListener("click", () => {
  const trapezoidalFunc = document.getElementById("function").value;
  const lowerLimit = document.getElementById("lower-limit").value;
  const upperLimit = document.getElementById("upper-limit-value").value;
  const intervals = document.getElementById("sub-intervals").value;

  if (!trapezoidalFunc || !lowerLimit || !upperLimit || !intervals) {
    alert("Please enter all values before calculating");
    return;
  }

  if (intervals <= 0) {
    alert("Number of intervals cannot be negative or 0");
  }

  fetch("/trapezoidal-rule-calci", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      F: trapezoidalFunc,
      lowerLimit: lowerLimit,
      upperLimit: upperLimit,
      subIntervals: intervals,
    }),
  })
    .then((response) => {
      if (response.ok) {
        return response.json();
      } else {
        throw new Error("Invalid Response");
      }
    })
    .then((data) => {
      document.querySelector(
        ".ans-text"
      ).textContent = `Result of Integration: ${data.toFixed(4)}`;
    })
    .catch((error) => {
      alert("An Error Occured. Try checking your function/values for mistakes");
    });
});

resetButton.addEventListener("click", () => {
  document.getElementById("function").value = "";
  document.getElementById("lower-limit").value = "";
  document.getElementById("upper-limit-value").value = "";
  document.getElementById("sub-intervals").value = "";
  document.querySelector(".ans-text").textContent = "";
});
