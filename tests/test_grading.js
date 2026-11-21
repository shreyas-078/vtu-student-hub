// Run: node tests/test_grading.js
// Every expected value is an illustration printed in VTU's own regulations.
const assert = require("assert");
const G = require("../static/js/vtu-grading.js");
let n = 0;
const t = (name, fn) => { fn(); n++; console.log("ok  " + name); };

t("2015 SGPA illustration rows: credit points 27+18+18+12", () => {
  const r = G.sgpa([{ credits: 3, gp: 9 }, { credits: 3, gp: 6 }, { credits: 2, gp: 9 }, { credits: 2, gp: 6 }]);
  assert.strictEqual(r.credits, 10); assert.strictEqual(r.creditPoints, 75);
});
t("2015 SGPA from printed total 189/25", () => assert.strictEqual(G.round2(189 / 25), 7.56));
t("2015 CGPA two semesters: 7.26", () =>
  assert.strictEqual(G.cgpa([{ credits: 25, sgpa: 6.96 }, { credits: 25, sgpa: 7.56 }]).cgpa, 7.26));
t("2015/2017/2018 eight-semester CGPA: 8.2", () => {
  const cr = [24, 24, 27, 27, 24, 24, 24, 26], sg = [7, 8.5, 9.2, 6.86, 8.18, 7.73, 8.68, 9.4];
  assert.strictEqual(G.cgpa(cr.map((credits, i) => ({ credits, sgpa: sg[i] }))).cgpa, 8.2);
});
t("2025 SGPA example: 101/20 = 5.05 (F courses count)", () => {
  const rows = [[3,8],[3,0],[3,9],[3,0],[3,6],[1,5],[1,9],[2,6],[1,6]];
  const r = G.sgpa(rows.map(([credits, gp]) => ({ credits, gp })));
  assert.strictEqual(r.credits, 20); assert.strictEqual(r.creditPoints, 101);
  assert.strictEqual(r.sgpa, 5.05);
});
t("2025 CGPA example: 1406/160 = 8.79", () => {
  const crp = [101, 178, 220, 165, 204, 185, 184, 169], cr = [20,20,20,20,20,20,24,16];
  const r = G.cgpa(cr.map((credits, i) => ({ credits, sgpa: crp[i] / credits })));
  assert.strictEqual(r.credits, 160); assert.strictEqual(r.cgpa, 8.79);
});
t("2025 lateral entry CGPA: 1127/120 = 9.39", () => {
  const crp = [220, 165, 204, 185, 184, 169], cr = [20,20,20,20,24,16];
  assert.strictEqual(G.cgpa(cr.map((credits, i) => ({ credits, sgpa: crp[i] / credits }))).cgpa, 9.39);
});
t("Percentage, CGPA 8.20: 82.0 (2021+) and 74.5 (2015/17/18)", () => {
  for (const k of ["2021", "2022", "2025"]) assert.strictEqual(G.toPercent(k, 8.2), 82);
  for (const k of ["2015", "2017", "2018"]) assert.strictEqual(G.toPercent(k, 8.2), 74.5);
});
t("Class bands 2021+: 70 FCD, 60 FC, 50 SC, 40 Pass, below none", () => {
  assert.strictEqual(G.classFor("2022", 70), "First Class with Distinction");
  assert.strictEqual(G.classFor("2022", 69.99), "First Class");
  assert.strictEqual(G.classFor("2022", 50), "Second Class");
  assert.strictEqual(G.classFor("2022", 40), "Pass Class");
  assert.strictEqual(G.classFor("2022", 39.9), "Below the pass-class threshold");
});
t("Class bands 2017/2018: below 60 is Second Class; 2015 has none", () => {
  assert.strictEqual(G.classFor("2018", 45), "Second Class");
  assert.strictEqual(G.classFor("2015", 80), null);
});
t("2021+ grade bands incl. boundaries", () => {
  const e = [[100,"O",10],[90,"O",10],[89,"A+",9],[80,"A+",9],[79,"A",8],[70,"A",8],[69,"B+",7],
    [60,"B+",7],[59,"B",6],[55,"B",6],[54,"C",5],[50,"C",5],[49,"P",4],[40,"P",4],[39,"F",0],[0,"F",0]];
  for (const [p, l, gp] of e) assert.deepStrictEqual(G.gradeForPercent("2022", p), { letter: l, gp });
});
t("2017/2018 grade bands incl. boundaries", () => {
  const e = [[90,"S",10],[89,"A",9],[80,"A",9],[79,"B",8],[70,"B",8],[69,"C",7],[60,"C",7],
    [59,"D",6],[45,"D",6],[44,"E",4],[40,"E",4],[39,"F",0]];
  for (const [p, l, gp] of e) assert.deepStrictEqual(G.gradeForPercent("2018", p), { letter: l, gp });
});
t("2015 grade bands incl. D=5 and E=4", () => {
  const e = [[90,"O",10],[80,"S",9],[70,"A",8],[60,"B",7],[50,"C",6],[45,"D",5],[44,"E",4],[40,"E",4],[39,"F",0]];
  for (const [p, l, gp] of e) assert.deepStrictEqual(G.gradeForPercent("2015", p), { letter: l, gp });
});
t("2022: CIE 19/50 fails even with a high total", () => {
  const r = G.courseFromCieSee("2022", 19, 100);
  assert.strictEqual(r.letter, "F"); assert.ok(r.reasons[0].includes("CIE"));
});
t("2022: SEE below 18/50 fails; 18/50 passes (raw 35/100 scales to 18)", () => {
  assert.strictEqual(G.courseFromCieSee("2022", 50, 34).letter, "F");
  const r = G.courseFromCieSee("2022", 50, 35);
  assert.strictEqual(r.see, 18); assert.strictEqual(r.total, 68); assert.strictEqual(r.letter, "B+");
});
t("2022: CIE 20 + SEE 20/50 = 40 passes as P", () => {
  const r = G.courseFromCieSee("2022", 20, 40);
  assert.strictEqual(r.total, 40); assert.strictEqual(r.letter, "P");
});
t("2022: SEE 18/50 with CIE 20 totals 38, fails the 40% total", () => {
  const r = G.courseFromCieSee("2022", 20, 36);
  assert.strictEqual(r.total, 38); assert.strictEqual(r.letter, "F");
});
t("2018: CIE minimum 16/40; 2017 has no CIE minimum for theory", () => {
  assert.strictEqual(G.courseFromCieSee("2018", 15, 100).letter, "F");
  assert.strictEqual(G.courseFromCieSee("2018", 16, 100).letter, "B");
  assert.strictEqual(G.courseFromCieSee("2017", 5, 100).letter, "C");
});
t("2018: SEE 100 scales to 60; minimum 21/60", () => {
  assert.strictEqual(G.courseFromCieSee("2018", 40, 100).total, 100);
  assert.strictEqual(G.courseFromCieSee("2018", 40, 34).letter, "F");
  assert.strictEqual(G.courseFromCieSee("2018", 40, 35).letter, "C");
});
t("Planner: from 7.5 over 100 credits, 8.0 over 100 more needs 8.5", () => {
  const r = G.requiredSgpa(100, 7.5, 100, 8.0);
  assert.strictEqual(r.needed, 8.5); assert.ok(r.reachable);
  assert.ok(!G.requiredSgpa(100, 7.5, 20, 9.5).reachable);
});
t("Invalid input throws", () => {
  assert.throws(() => G.gradeForPercent("2022", 101));
  assert.throws(() => G.courseFromCieSee("2015", 10, 50));
  assert.throws(() => G.scheme("1999"));
});
console.log("\n" + n + " tests passed");
