const calculateButton = document.querySelector(".calculate-btn");
const resetButton = document.querySelector(".reset-btn");

calculateButton.addEventListener("click", () => {
  const simpson13Func = document.querySelector("#function").value;
  const lowerLimit = document.getElementById("lower-limit").value;
  const upperLimit = document.getElementById("upper-limit-value").value;
  const intervals = document.getElementById("sub-intervals").value;

  if (!simpson13Func || !lowerLimit || !upperLimit || !intervals) {
    alert("Please enter all values before calculating.");
    return;
  }

  if (intervals % 3 != 0) {
    alert("Number of sub intervals should be a multiple of 3");
    return;
  }

  fetch("/simpson-3-8-calci", {
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
      alert("An Error Occured. Try again with different values.");
    });
});

resetButton.addEventListener("click", () => {
  document.querySelector("#function").value = "";
  document.getElementById("lower-limit").value = "";
  document.getElementById("upper-limit-value").value = "";
  document.getElementById("sub-intervals").value = "";
  document.querySelector(".ans-text").innerHTML = "";
});
