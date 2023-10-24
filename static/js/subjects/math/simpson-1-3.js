const calculateButton = document.querySelector(".calculate-btn");

calculateButton.addEventListener("click", () => {
  const simpson13Func = document.getElementById("function").value;
  const lowerLimit = document.getElementById("lower-limit").value;
  const upperLimit = document.getElementById("upper-limit-value").value;
  const intervals = document.getElementById("sub-intervals").value;

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
    });
});
