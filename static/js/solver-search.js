(function () {
  var q = document.getElementById("solver-q");
  if (!q) return;
  var items = Array.prototype.slice.call(document.querySelectorAll("[data-solver]"));
  var count = document.getElementById("solver-count");
  var none = document.getElementById("solver-none");

  function run() {
    var words = q.value.toLowerCase().split(/\s+/).filter(Boolean);
    var shown = 0;
    items.forEach(function (li) {
      var hit = words.every(function (w) { return li.dataset.text.indexOf(w) !== -1; });
      li.hidden = !hit;
      if (hit) shown++;
    });
    document.querySelectorAll("[data-group]").forEach(function (g) {
      g.hidden = !g.querySelector("[data-solver]:not([hidden])");
    });
    document.querySelectorAll("[data-subject]").forEach(function (s) {
      s.hidden = !s.querySelector("[data-solver]:not([hidden])");
    });
    none.classList.toggle("invisible", shown !== 0);
    count.textContent = words.length ? shown + " of " + items.length + " calculators" : "";
  }
  q.addEventListener("input", run);
  var param = new URLSearchParams(location.search).get("q");
  if (param) { q.value = param; run(); }
})();
