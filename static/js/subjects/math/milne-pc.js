const mpcCalculateButton = document.querySelector(".btn-milne-pc-answer");
const mpcClearButton = document.querySelector(".btn-milne-pc-clear");

mpcCalculateButton.addEventListener("click", () => {
    const mpcFunction = document.querySelector(
        "#milne-pc-function-input"
    ).value;
    const mpcX0 = document.querySelector("#milne-pc-x0-input").value;
    const mpcY0 = document.querySelector("#milne-pc-y0-input").value;
    const mpcX1 = document.querySelector("#milne-pc-x1-input").value;
    const mpcY1 = document.querySelector("#milne-pc-y1-input").value;
    const mpcX2 = document.querySelector("#milne-pc-x2-input").value;
    const mpcY2 = document.querySelector("#milne-pc-y2-input").value;
    const mpcX3 = document.querySelector("#milne-pc-x3-input").value;
    const mpcY3 = document.querySelector("#milne-pc-y3-input").value;

    fetch("/milne-pc", {
        method: "POST",
        headers: { ContentType: "application/json" },
        body: JSON.stringify({
            f: mpcFunction,
            x0: mpcX0,
            y0: mpcY0,
            x1: mpcX1,
            y1: mpcY1,
            x2: mpcX2,
            y2: mpcY2,
            x3: mpcX3,
            y3: mpcY3,
        }),
    }).then((response) => {
        if (response.ok) {
            console.log(response.json());
            return response.json().then((data) => {});
        } else {
            console.error("Error:", response.status, response.statusText);
        }
    });
});
