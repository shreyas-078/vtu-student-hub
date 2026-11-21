/* SGPA / CGPA / percentage calculator UI. Rules live in vtu-grading.js. */
(function () {
  "use strict";
  const G = window.VTUGrading;
  const KEY = "vtuhub.gpa.v1";
  const $ = (id) => document.getElementById(id);

  const blankCourse = () => ({ name: "", credits: "3", cie: "", see: "", total: "", letter: "" });
  const blankSem = () => ({ credits: "", sgpa: "" });
  let state = {
    scheme: "2022", mode: "cie-see", lateral: false,
    courses: [blankCourse(), blankCourse(), blankCourse(), blankCourse(), blankCourse()],
    sems: [blankSem(), blankSem()],
    pctCgpa: "", pctTouched: false, planTarget: "", planCredits: "",
  };

  function load() {
    try {
      const saved = JSON.parse(localStorage.getItem(KEY));
      if (saved && G.SCHEMES[saved.scheme] && Array.isArray(saved.courses) && Array.isArray(saved.sems)) {
        state = Object.assign(state, saved);
        if (!state.courses.length) state.courses = [blankCourse()];
        if (!state.sems.length) state.sems = [blankSem()];
      }
    } catch (e) { /* private mode or corrupt data: start fresh */ }
  }
  function save() {
    try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) { /* ignore */ }
  }

  function h(tag, attrs, ...kids) {
    const el = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs || {})) {
      if (k === "class") el.className = v;
      else if (k === "text") el.textContent = v;
      else if (v === true) el.setAttribute(k, "");
      else if (v !== false && v != null) el.setAttribute(k, v);
    }
    for (const kid of kids) if (kid != null) el.append(kid);
    return el;
  }
  const num = (s) => (s === "" || s == null ? NaN : Number(s));
  const fmt = (x) => (Number.isInteger(x) ? String(x) : String(G.round2(x)));
  const scheme = () => G.scheme(state.scheme);

  /* ---- scheme summary and grade table ------------------------------------ */
  function renderScheme() {
    const s = scheme();
    const pct = s.percent === "x10" ? "percentage = CGPA × 10" : "percentage = (CGPA − 0.75) × 10";
    const parts = s.cie === null
      ? "Marks are entered as a total or letter grade."
      : "CIE " + s.cie + " + SEE " + s.see + " (paper of 100 scaled to " + s.see + ").";
    $("scheme-summary").textContent = G.letters(state.scheme).join(", ") + " grades. " + parts + " " + pct[0].toUpperCase() + pct.slice(1) + ".";

    const rows = s.scale.map((b, i) => {
      const hi = i === 0 ? 100 : s.scale[i - 1][0] - 1;
      return h("tr", {}, h("th", { scope: "row", text: b[1] }), h("td", { text: String(b[2]) }),
        h("td", { text: b[0] + " to " + hi }));
    });
    $("grade-table").replaceChildren(h("table", {},
      h("thead", {}, h("tr", {}, h("th", { scope: "col", text: "Grade" }), h("th", { scope: "col", text: "Grade point" }),
        h("th", { scope: "col", text: "% of marks" }))),
      h("tbody", {}, ...rows)));
  }

  /* ---- SGPA ---------------------------------------------------------------- */
  const MODE_HELP = {
    "cie-see": () => "Enter CIE out of " + scheme().cie + " and the SEE paper marks out of 100 (as on your result). The pass rules are applied for you.",
    total: () => "Enter the total out of 100. Pass rules cannot be checked from a total alone, so a total of 40 or more passes.",
    grade: () => "Pick the letter grade printed on your grade card.",
  };

  function evalCourse(c) {
    const credits = num(c.credits);
    if (!(credits >= 0 && credits <= 20)) return { state: "incomplete", why: "Credits needed" };
    let r;
    try {
      if (state.mode === "grade") {
        if (!c.letter) return { state: "incomplete", why: "Pick a grade" };
        r = { letter: c.letter, gp: G.gradePointForLetter(state.scheme, c.letter) };
        r.passed = r.letter !== "F"; r.reasons = [];
      } else if (state.mode === "total") {
        const t = num(c.total);
        if (Number.isNaN(t)) return { state: "incomplete", why: "Marks needed" };
        r = G.courseFromTotal(state.scheme, t);
      } else {
        const cie = num(c.cie), see = num(c.see);
        if (Number.isNaN(cie) || Number.isNaN(see)) return { state: "incomplete", why: "CIE and SEE needed" };
        r = G.courseFromCieSee(state.scheme, cie, see);
      }
    } catch (e) {
      return { state: "error", why: e.message };
    }
    return { state: "ok", credits, r };
  }

  function field(label, input) {
    return h("div", { class: "f" }, h("label", {}, label), input);
  }

  function renderCourses() {
    const s = scheme();
    const list = $("courses");
    list.replaceChildren();
    state.courses.forEach((c, i) => {
      const bind = (el, prop) => el.addEventListener("input", () => { c[prop] = el.value; update(); });
      const id = "c" + i;
      const nameIn = h("input", { type: "text", id: id + "n", value: c.name, placeholder: "Subject " + (i + 1), autocomplete: "off", maxlength: "40" });
      const crIn = h("input", { type: "number", id: id + "c", value: c.credits, min: "0", max: "20", step: "0.5", inputmode: "decimal" });
      bind(nameIn, "name"); bind(crIn, "credits");
      const fields = [];
      if (state.mode === "cie-see") {
        const a = h("input", { type: "number", id: id + "a", value: c.cie, min: "0", max: String(s.cie), step: "1", inputmode: "numeric", placeholder: "0 to " + s.cie });
        const b = h("input", { type: "number", id: id + "b", value: c.see, min: "0", max: "100", step: "1", inputmode: "numeric", placeholder: "0 to 100" });
        bind(a, "cie"); bind(b, "see");
        fields.push(field("CIE (of " + s.cie + ")", a), field("SEE (of 100)", b));
      } else if (state.mode === "total") {
        const t = h("input", { type: "number", id: id + "t", value: c.total, min: "0", max: "100", step: "1", inputmode: "numeric", placeholder: "0 to 100" });
        bind(t, "total");
        fields.push(field("Total (of 100)", t));
      } else {
        const sel = h("select", { id: id + "g" }, h("option", { value: "", text: "Choose" }),
          ...G.letters(state.scheme).map((l) => h("option", { value: l, text: l + " (" + G.gradePointForLetter(state.scheme, l) + ")" })));
        sel.value = c.letter;
        bind(sel, "letter");
        sel.addEventListener("change", () => { c.letter = sel.value; update(); });
        fields.push(field("Grade", sel));
      }
      const out = h("div", { class: "course-out" }, h("output", { id: id + "o", for: id + "n" }), h("p", { class: "why", id: id + "w" }));
      const rm = h("button", { type: "button", class: "remove", "aria-label": "Remove subject " + (i + 1), text: "Remove" });
      rm.addEventListener("click", () => {
        state.courses.splice(i, 1);
        if (!state.courses.length) state.courses.push(blankCourse());
        renderCourses(); update();
      });
      list.append(h("li", { class: "course" },
        h("div", { class: "course-fields" }, field("Subject", nameIn), field("Credits", crIn), ...fields), out, rm));
    });
    $("mode-help").textContent = MODE_HELP[state.mode]();
  }

  function updateSgpa() {
    const ok = [];
    let incomplete = 0, errors = 0;
    state.courses.forEach((c, i) => {
      const e = evalCourse(c);
      const out = $("c" + i + "o"), why = $("c" + i + "w");
      const item = out && out.closest(".course");
      if (!out) return;
      item.classList.toggle("fail", e.state === "ok" && !e.r.passed);
      if (e.state === "ok") {
        ok.push({ credits: e.credits, gp: e.r.gp, passed: e.r.passed, name: c.name || "Subject " + (i + 1), reasons: e.r.reasons });
        out.textContent = e.r.letter + " · " + e.r.gp + " pts · " + fmt(e.credits * e.r.gp) + " credit pts";
        why.textContent = e.r.reasons.join(". ");
      } else {
        if (e.state === "error") errors++; else incomplete++;
        out.textContent = "";
        why.textContent = e.state === "error" ? e.why : "";
        const touched = state.mode === "cie-see" ? c.cie || c.see : state.mode === "total" ? c.total : c.letter;
        if (e.state === "incomplete" && touched) why.textContent = e.why;
      }
    });
    const box = $("sgpa-result");
    box.classList.remove("empty");
    if (!ok.length) {
      box.replaceChildren(h("p", { class: "placeholder", text: "Fill in at least one subject to see your SGPA." }));
      state.sgpaValue = null; save(); updateCgpaButton(); return;
    }
    const r = G.sgpa(ok);
    state.sgpaValue = r.sgpa; state.sgpaCredits = r.credits;
    const failed = ok.filter((x) => !x.passed);
    const kids = [
      h("p", { class: "big" }, h("span", { class: "k", text: "SGPA " }), h("span", { class: "v", text: r.sgpa === null ? "n/a" : r.sgpa.toFixed(2) })),
      h("p", { class: "meta", text: fmt(r.creditPoints) + " credit points over " + fmt(r.credits) + " credits, from " + ok.length + " of " + state.courses.length + " subjects." }),
    ];
    if (r.credits === 0) kids.push(h("p", { class: "warn", text: "Every counted subject has zero credits, so there is no SGPA to show." }));
    if (incomplete + errors) kids.push(h("p", { class: "warn", text: (incomplete + errors) + " subject" + (incomplete + errors > 1 ? "s are" : " is") + " incomplete and not counted. The SGPA above is partial." }));
    if (failed.length) kids.push(h("p", { class: "warn", text: failed.length + " subject" + (failed.length > 1 ? "s" : "") + " with an F (" + failed.map((x) => x.name).join(", ") + "). You must reappear for " + (failed.length > 1 ? "them" : "it") + "." }));
    box.replaceChildren(...kids);
    save(); updateCgpaButton();
  }

  /* ---- CGPA ---------------------------------------------------------------- */
  const firstSem = () => (state.lateral ? 3 : 1);

  function renderSems() {
    const list = $("semesters");
    list.replaceChildren();
    state.sems.forEach((s, i) => {
      const cr = h("input", { type: "number", id: "s" + i + "c", value: s.credits, min: "0", max: "40", step: "0.5", inputmode: "decimal", placeholder: "e.g. 20" });
      const sg = h("input", { type: "number", id: "s" + i + "g", value: s.sgpa, min: "0", max: "10", step: "0.01", inputmode: "decimal", placeholder: "e.g. 8.25" });
      cr.addEventListener("input", () => { s.credits = cr.value; updateCgpa(); });
      sg.addEventListener("input", () => { s.sgpa = sg.value; updateCgpa(); });
      const rm = h("button", { type: "button", class: "remove", "aria-label": "Remove semester " + (firstSem() + i), text: "Remove" });
      rm.addEventListener("click", () => {
        state.sems.splice(i, 1);
        if (!state.sems.length) state.sems.push(blankSem());
        renderSems(); updateCgpa();
      });
      list.append(h("li", { class: "semester" }, h("p", { class: "sem-label", text: "Semester " + (firstSem() + i) }),
        field("Credits", cr), field("SGPA", sg), rm));
    });
  }

  function validSems() {
    return state.sems.filter((s) => num(s.credits) > 0 && num(s.sgpa) >= 0 && num(s.sgpa) <= 10)
      .map((s) => ({ credits: num(s.credits), sgpa: num(s.sgpa) }));
  }

  function updateCgpa() {
    const sems = validSems();
    const box = $("cgpa-result");
    if (!sems.length) {
      box.replaceChildren(h("p", { class: "placeholder", text: "Enter credits and SGPA for at least one semester." }));
      state.cgpaValue = null;
    } else {
      const r = G.cgpa(sems);
      state.cgpaValue = r.cgpa; state.cgpaCredits = r.credits;
      const kids = [
        h("p", { class: "big" }, h("span", { class: "k", text: "CGPA " }), h("span", { class: "v", text: r.cgpa.toFixed(2) })),
        h("p", { class: "meta", text: "Over " + fmt(r.credits) + " credits in " + sems.length + " semester" + (sems.length > 1 ? "s" : "") + "." }),
      ];
      const skipped = state.sems.length - sems.length;
      if (skipped) kids.push(h("p", { class: "warn", text: skipped + " semester row" + (skipped > 1 ? "s are" : " is") + " blank or invalid and not counted." }));
      box.replaceChildren(...kids);
    }
    if (!state.pctTouched) {
      state.pctCgpa = state.cgpaValue == null ? "" : String(state.cgpaValue.toFixed(2));
      $("pct-cgpa").value = state.pctCgpa;
      updatePct();
    }
    updatePlan(); save();
  }

  function updateCgpaButton() {
    const b = $("use-sgpa");
    b.hidden = state.sgpaValue == null;
    if (state.sgpaValue != null) b.textContent = "Add my SGPA " + state.sgpaValue.toFixed(2) + " from the SGPA tab";
  }

  function updatePlan() {
    const box = $("plan-result");
    const t = num(state.planTarget), rc = num(state.planCredits);
    if (state.cgpaValue == null || !(t >= 0 && t <= 10) || !(rc > 0)) {
      box.replaceChildren(h("p", { class: "placeholder", text: state.cgpaValue == null ? "Calculate a CGPA above first, then enter a target and the credits still to go." : "Enter a target CGPA (0 to 10) and the credits still to go." }));
      return;
    }
    const r = G.requiredSgpa(state.cgpaCredits, state.cgpaValue, rc, t);
    let msg;
    if (r.alreadyMet) msg = "You already clear " + t.toFixed(2) + ". Any SGPA keeps you at or above it.";
    else if (!r.reachable) msg = "Not reachable. It would need an SGPA of " + r.needed.toFixed(2) + ", and the maximum is 10. The best you can end on is " + G.round2((state.cgpaValue * state.cgpaCredits + 10 * rc) / (state.cgpaCredits + rc)).toFixed(2) + ".";
    else msg = "You need an SGPA of " + (Math.ceil(r.needed * 100) / 100).toFixed(2) + " or better, on average, over the next " + fmt(rc) + " credits.";
    box.replaceChildren(h("p", { text: msg }));
  }

  /* ---- percentage -------------------------------------------------------------- */
  function updatePct() {
    const box = $("pct-result");
    const s = scheme();
    const c = num(state.pctCgpa);
    if (!(c >= 0 && c <= 10)) {
      box.replaceChildren(h("p", { class: "placeholder", text: "Enter a CGPA between 0 and 10, or calculate one in the CGPA tab." }));
    } else {
      const p = G.toPercent(state.scheme, c);
      const formula = s.percent === "x10" ? c.toFixed(2) + " × 10" : "(" + c.toFixed(2) + " − 0.75) × 10";
      const cls = G.classFor(state.scheme, p);
      box.replaceChildren(
        h("p", { class: "big" }, h("span", { class: "k", text: "Percentage " }), h("span", { class: "v", text: p.toFixed(2) + "%" })),
        h("p", { class: "meta", text: formula + " = " + p.toFixed(2) + "%" }),
        h("p", { class: "meta", text: cls ? "Class on this percentage: " + cls + "." : "The 2015 regulations I read do not define class bands." }));
    }
    $("pct-note").textContent = s.percent === "x10"
      ? "For the " + state.scheme + " scheme VTU converts with CGPA × 10. The (CGPA − 0.75) × 10 formula you may see elsewhere is for the 2015, 2017 and 2018 schemes only."
      : "For the " + state.scheme + " scheme VTU converts with (CGPA − 0.75) × 10. Later schemes (2021 onward) use CGPA × 10. Class applies to the final CGPA after completing the programme.";
  }

  function cgpaNote() {
    const m = scheme().cgpa;
    $("cgpa-note").textContent =
      m === "excluding-F" ? "For this scheme VTU leaves subjects holding an F out of the CGPA. This tab uses printed SGPAs, so it is exact only with no outstanding F."
      : m === "passed-courses" ? "For this scheme VTU takes the CGPA over courses successfully completed. This tab uses printed SGPAs, so it is exact only with no outstanding F."
      : "For this scheme VTU averages over all courses undergone. Cleared backlogs carry the re-attempt grade.";
  }

  /* ---- wiring -------------------------------------------------------------- */
  function update() { updateSgpa(); }

  function showTab(name) {
    for (const t of ["sgpa", "cgpa", "pct"]) {
      const on = t === name;
      $("tab-" + t).setAttribute("aria-selected", on ? "true" : "false");
      $("tab-" + t).tabIndex = on ? 0 : -1;
      $("panel-" + t).hidden = !on;
    }
  }

  function init() {
    load();
    $("scheme").value = state.scheme;
    document.querySelector('input[name="mode"][value="' + state.mode + '"]').checked = true;
    $("lateral").checked = state.lateral;
    $("plan-target").value = state.planTarget;
    $("plan-credits").value = state.planCredits;
    $("pct-cgpa").value = state.pctCgpa;

    const applyScheme = () => {
      if (scheme().cie === null) {
        const r = document.querySelector('input[name="mode"][value="cie-see"]');
        r.disabled = true;
        if (state.mode === "cie-see") {
          state.mode = "total";
          document.querySelector('input[name="mode"][value="total"]').checked = true;
        }
      } else {
        document.querySelector('input[name="mode"][value="cie-see"]').disabled = false;
      }
      // Letters differ between schemes, so any chosen letter may no longer exist.
      state.courses.forEach((c) => { if (c.letter && G.gradePointForLetter(state.scheme, c.letter) === null) c.letter = ""; });
      renderScheme(); renderCourses(); updateSgpa(); cgpaNote(); updateCgpa(); updatePct();
    };

    $("scheme").addEventListener("change", (e) => { state.scheme = e.target.value; applyScheme(); });
    document.querySelectorAll('input[name="mode"]').forEach((r) =>
      r.addEventListener("change", () => { if (r.checked) { state.mode = r.value; renderCourses(); updateSgpa(); } }));
    $("add-course").addEventListener("click", () => {
      if (state.courses.length >= 20) return;
      state.courses.push(blankCourse()); renderCourses(); updateSgpa();
      const last = state.courses.length - 1; $("c" + last + "n").focus();
    });
    $("reset-sgpa").addEventListener("click", () => {
      state.courses = [blankCourse(), blankCourse(), blankCourse(), blankCourse(), blankCourse()];
      renderCourses(); updateSgpa();
    });
    $("lateral").addEventListener("change", (e) => { state.lateral = e.target.checked; renderSems(); save(); });
    $("add-sem").addEventListener("click", () => {
      if (state.sems.length >= 8) return;
      state.sems.push(blankSem()); renderSems(); updateCgpa();
      $("s" + (state.sems.length - 1) + "c").focus();
    });
    $("use-sgpa").addEventListener("click", () => {
      if (state.sgpaValue == null) return;
      const empty = state.sems.findIndex((s) => s.credits === "" && s.sgpa === "");
      const row = { credits: String(state.sgpaCredits), sgpa: state.sgpaValue.toFixed(2) };
      if (empty >= 0) state.sems[empty] = row; else if (state.sems.length < 8) state.sems.push(row);
      renderSems(); updateCgpa();
    });
    $("reset-cgpa").addEventListener("click", () => {
      state.sems = [blankSem(), blankSem()]; state.pctTouched = false;
      renderSems(); updateCgpa();
    });
    $("plan-target").addEventListener("input", (e) => { state.planTarget = e.target.value; updatePlan(); save(); });
    $("plan-credits").addEventListener("input", (e) => { state.planCredits = e.target.value; updatePlan(); save(); });
    $("pct-cgpa").addEventListener("input", (e) => {
      state.pctCgpa = e.target.value; state.pctTouched = e.target.value !== ""; updatePct(); save();
    });

    const tabs = ["sgpa", "cgpa", "pct"];
    tabs.forEach((t, i) => {
      $("tab-" + t).addEventListener("click", () => showTab(t));
      $("tab-" + t).addEventListener("keydown", (e) => {
        if (e.key !== "ArrowRight" && e.key !== "ArrowLeft") return;
        const n = tabs[(i + (e.key === "ArrowRight" ? 1 : tabs.length - 1)) % tabs.length];
        showTab(n); $("tab-" + n).focus();
      });
    });

    renderSems();
    applyScheme();
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
