/*
 * VTU grading rules: pure functions, no DOM access.
 * Loaded by the browser (window.VTUGrading) and by node (tests/test_grading.js).
 *
 * Every number here comes from VTU's own B.E./B.Tech regulations:
 *   2015: 15OB 11, 15OB 12          2017: 17OB 6.0, 7.0, 9.1
 *   2018: 18OB 6.0, 7.0, 8.0        2021: 21OB12.2, 21OB13.1-13.3
 *   2022: clauses 6.1-6.8           2025: 25OB22.0, 25OB25.0-27.0
 * See the "Sources" section of the calculator page for the full list.
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.VTUGrading = factory();
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  // Each band is [minimum percentage, letter, grade point], highest first.
  const SCALE_2015 = [
    [90, "O", 10], [80, "S", 9], [70, "A", 8], [60, "B", 7],
    [50, "C", 6], [45, "D", 5], [40, "E", 4], [0, "F", 0],
  ];
  const SCALE_2017 = [
    [90, "S", 10], [80, "A", 9], [70, "B", 8], [60, "C", 7],
    [45, "D", 6], [40, "E", 4], [0, "F", 0],
  ];
  const SCALE_2021 = [
    [90, "O", 10], [80, "A+", 9], [70, "A", 8], [60, "B+", 7],
    [55, "B", 6], [50, "C", 5], [40, "P", 4], [0, "F", 0],
  ];

  const CLASSES_4 = [[70, "First Class with Distinction"], [60, "First Class"],
                     [50, "Second Class"], [40, "Pass Class"]];
  const CLASSES_3 = [[70, "First Class with Distinction"], [60, "First Class"],
                     [0, "Second Class"]];

  /*
   * cie / see: maximum marks. The SEE paper is set for 100 and scaled down
   * to `see`. minCie: fraction of CIE needed to be allowed to pass (0 = none).
   */
  const SCHEMES = {
    "2025": { label: "2025 scheme", scale: SCALE_2021, cie: 50, see: 50, minCie: 0.4,
              percent: "x10", classes: CLASSES_4, cgpa: "passed-courses",
              lateralCgpaFrom: 4 },
    "2022": { label: "2022 scheme", scale: SCALE_2021, cie: 50, see: 50, minCie: 0.4,
              percent: "x10", classes: CLASSES_4, cgpa: "excluding-F",
              lateralCgpaFrom: 4 },
    "2021": { label: "2021 scheme", scale: SCALE_2021, cie: 50, see: 50, minCie: 0.4,
              percent: "x10", classes: CLASSES_4, cgpa: "excluding-F",
              lateralCgpaFrom: 4 },
    "2018": { label: "2018 scheme", scale: SCALE_2017, cie: 40, see: 60, minCie: 0.4,
              percent: "minus075", classes: CLASSES_3, cgpa: "all",
              lateralCgpaFrom: 4 },
    "2017": { label: "2017 scheme", scale: SCALE_2017, cie: 40, see: 60, minCie: 0,
              percent: "minus075", classes: CLASSES_3, cgpa: "all",
              lateralCgpaFrom: 4 },
    "2015": { label: "2015 scheme", scale: SCALE_2015, cie: null, see: null, minCie: 0,
              percent: "minus075", classes: null, cgpa: "all",
              lateralCgpaFrom: 4 },
  };

  const SEE_MIN_FRACTION = 0.35;  // of the SEE maximum, every scheme
  const TOTAL_MIN_FRACTION = 0.4; // CIE + SEE together, every scheme

  function scheme(key) {
    const s = SCHEMES[key];
    if (!s) throw new Error("Unknown scheme: " + key);
    return s;
  }

  // Round half up to 2 decimals, as VTU reports SGPA/CGPA.
  function round2(x) {
    return Math.round((x + Number.EPSILON) * 100) / 100;
  }

  function gradeForPercent(key, percent) {
    if (!(percent >= 0 && percent <= 100)) throw new Error("Percentage must be 0 to 100");
    const band = scheme(key).scale.find((b) => percent >= b[0]);
    return { letter: band[1], gp: band[2] };
  }

  function gradePointForLetter(key, letter) {
    const band = scheme(key).scale.find((b) => b[1] === letter);
    return band ? band[2] : null;
  }

  function letters(key) {
    return scheme(key).scale.map((b) => b[1]);
  }

  /* A course from its total marks out of 100 (no pass checks are possible). */
  function courseFromTotal(key, total) {
    const g = gradeForPercent(key, total);
    return { total, letter: g.letter, gp: g.gp, passed: g.letter !== "F", reasons: [] };
  }

  /*
   * A course from CIE marks and SEE marks (SEE entered out of 100).
   * Applies the pass rules: minimum CIE, SEE >= 35%, total >= 40%.
   * Failing any of them is an F, whatever the total says.
   */
  function courseFromCieSee(key, cie, seeRaw) {
    const s = scheme(key);
    if (s.cie === null) throw new Error("CIE/SEE entry is not available for this scheme");
    if (!(cie >= 0 && cie <= s.cie)) throw new Error("CIE must be 0 to " + s.cie);
    if (!(seeRaw >= 0 && seeRaw <= 100)) throw new Error("SEE must be 0 to 100");

    // Paper marked out of 100, scaled to the scheme's SEE maximum.
    const see = Math.floor((seeRaw * s.see) / 100 + 0.5);
    const total = cie + see;
    const reasons = [];

    const cieNeeded = Math.ceil(s.minCie * s.cie - 1e-9);
    if (cie < cieNeeded) reasons.push("CIE " + cie + " is below the minimum " + cieNeeded + " of " + s.cie);

    const seeNeeded = Math.ceil(SEE_MIN_FRACTION * s.see - 1e-9);
    if (see < seeNeeded) reasons.push("SEE " + see + " is below the minimum " + seeNeeded + " of " + s.see);

    const totalNeeded = Math.ceil(TOTAL_MIN_FRACTION * (s.cie + s.see) - 1e-9);
    if (total < totalNeeded) reasons.push("Total " + total + " is below the minimum " + totalNeeded + " of " + (s.cie + s.see));

    if (reasons.length) return { total, see, letter: "F", gp: 0, passed: false, reasons };
    const g = gradeForPercent(key, (total * 100) / (s.cie + s.see));
    return { total, see, letter: g.letter, gp: g.gp, passed: g.letter !== "F", reasons };
  }

  /* SGPA = sum(credits x grade point) / sum(credits). F counts, with 0 points. */
  function sgpa(courses) {
    let credits = 0, points = 0;
    for (const c of courses) {
      if (!(c.credits >= 0)) throw new Error("Credits must be zero or more");
      credits += c.credits;
      points += c.credits * c.gp;
    }
    return { credits, creditPoints: points, sgpa: credits > 0 ? round2(points / credits) : null };
  }

  /*
   * CGPA from semesters [{credits, sgpa}]: sum(credits x SGPA) / sum(credits).
   * Correct when no F is outstanding. See the page note on F grades.
   */
  function cgpa(semesters) {
    let credits = 0, points = 0;
    for (const s of semesters) {
      credits += s.credits;
      points += s.credits * s.sgpa;
    }
    return { credits, creditPoints: points, cgpa: credits > 0 ? round2(points / credits) : null };
  }

  /* The SGPA needed in the remaining credits to end on a target CGPA. */
  function requiredSgpa(doneCredits, doneCgpa, remainingCredits, target) {
    if (!(remainingCredits > 0)) throw new Error("Remaining credits must be above zero");
    const needed = (target * (doneCredits + remainingCredits) - doneCgpa * doneCredits) / remainingCredits;
    return { needed, reachable: needed <= 10, alreadyMet: needed <= 0 };
  }

  function toPercent(key, cgpaValue) {
    const s = scheme(key);
    const pct = s.percent === "x10" ? cgpaValue * 10 : (cgpaValue - 0.75) * 10;
    return Math.max(0, round2(pct));
  }

  function classFor(key, percent) {
    const s = scheme(key);
    if (!s.classes) return null;
    const band = s.classes.find((b) => percent >= b[0]);
    return band ? band[1] : "Below the pass-class threshold";
  }

  return {
    SCHEMES, SEE_MIN_FRACTION, TOTAL_MIN_FRACTION,
    scheme, round2, letters, gradeForPercent, gradePointForLetter,
    courseFromTotal, courseFromCieSee, sgpa, cgpa, requiredSgpa, toPercent, classFor,
  };
});
