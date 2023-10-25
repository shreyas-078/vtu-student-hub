const calculateButton = document.querySelector(".calculate-btn");
const resetButton = document.querySelector(".reset-btn");

calculateButton.addEventListener("click", () => {
  const simpson13Func = document.getElementById("function").value;
  const lowerLimit = document.getElementById("lower-limit").value;
  const upperLimit = document.getElementById("upper-limit-value").value;
  const intervals = document.getElementById("sub-intervals").value;

  if (!simpson13Func || !lowerLimit || !upperLimit || !intervals) {
    alert("Please enter all values before calculating.");
    return;
  }

  if (intervals < 0) {
    alert("Number of intervals cannot be negative");
    return;
  }

  if (intervals % 2 != 0) {
    alert("Number of sub intervals must be divisible by 2");
    return;
  }

  fetch("/simpson-1-3-calci", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      F: simpson13Func,
      lowerLimit: lowerLimit,
      upperLimit: upperLimit,
      subIntervals: intervals,
    }),
  })
    .then((response) => {
      if (response.status === 500) {
        throw new Error("Try again");
      }
      if (response.ok) {
        return response.json();
      } else {
        console.error("Invalid Response");
      }
    })
    .then((data) => {
      document.querySelector(
        ".ans-text"
      ).textContent = `Result of Integration: ${data.toFixed(4)}`;
    })
    .catch((error) => {
      alert("An Error Occured. Try Again with different values");
    });
});

resetButton.addEventListener("click", () => {
  document.getElementById("function").value = "";
  document.getElementById("lower-limit").value = "";
  document.getElementById("upper-limit-value").value = "";
  document.getElementById("sub-intervals").value = "";
  document.querySelector(".ans-text").innerHTML = "";
});
