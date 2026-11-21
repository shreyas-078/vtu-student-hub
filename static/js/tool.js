(function () {
  var form = document.getElementById("tool-form");
  var box = document.getElementById("tool-result");
  if (!form) return;
  var example = JSON.parse(form.dataset.example);
  var defaults = {};
  Array.prototype.forEach.call(form.elements, function (el) {
    if (el.name) defaults[el.name] = el.value;
  });

  function setValues(values) {
    Object.keys(defaults).forEach(function (k) {
      var el = form.elements[k];
      el.value = values[k] !== undefined ? values[k] : defaults[k];
    });
  }

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text !== undefined) n.textContent = text;
    return n;
  }

  function show(data) {
    box.replaceChildren();
    box.className = "";
    if (data.summary.length) {
      var dl = el("dl", "answers");
      data.summary.forEach(function (row) {
        dl.appendChild(el("dt", "", row[0]));
        dl.appendChild(el("dd", "", row[1]));
      });
      box.appendChild(dl);
    }
    data.notes.forEach(function (t) { box.appendChild(el("p", "result-note", t)); });
    data.tables.forEach(function (t) {
      box.appendChild(el("h2", "table-title", t.title));
      var wrap = el("div", "table-wrap");
      var table = el("table");
      var head = el("tr");
      t.columns.forEach(function (c) { head.appendChild(el("th", "", c)); });
      table.appendChild(el("thead")).appendChild(head);
      var body = el("tbody");
      t.rows.forEach(function (r) {
        var tr = el("tr");
        r.forEach(function (c) { tr.appendChild(el("td", "", c)); });
        body.appendChild(tr);
      });
      table.appendChild(body);
      wrap.appendChild(table);
      box.appendChild(wrap);
    });
  }

  function fail(msg) {
    box.replaceChildren(el("p", "result-error", msg));
    box.className = "has-error";
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var body = {};
    Array.prototype.forEach.call(form.elements, function (x) {
      if (x.name) body[x.name] = x.value;
    });
    fetch("/api/tools/" + form.dataset.slug, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    })
      .then(function (r) { return r.json().then(function (j) { return [r.ok, j]; }); })
      .then(function (res) {
        if (res[0]) show(res[1]); else fail(res[1].error || "Something went wrong");
        box.focus({ preventScroll: true });
        box.scrollIntoView({ behavior: "smooth", block: "nearest" });
      })
      .catch(function () { fail("Could not reach the server. Check your connection."); });
  });

  document.getElementById("tool-example").addEventListener("click", function () {
    setValues(example);
    form.requestSubmit();
  });
  document.getElementById("tool-reset").addEventListener("click", function () {
    setValues({});
    box.replaceChildren();
  });
})();
