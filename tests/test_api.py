import math
import time

import pytest

from app import PAGES, app


@pytest.fixture
def client():
    return app.test_client()


def call(client, path, data):
    return client.post(path, json=data)


def test_pages_render(client):
    for path in PAGES:
        assert client.get(path).status_code == 200, path


def test_trapezoidal_matches_known_value(client):
    r = call(client, "/trapezoidal-rule-calci",
             {"F": "1/(1+x**2)", "lowerLimit": 0, "upperLimit": 1, "subIntervals": 6})
    assert r.get_json() == pytest.approx(0.784241, abs=1e-5)


def test_simpson_rules_approximate_pi_over_4(client):
    for path in ("/simpson-1-3-calci", "/simpson-3-8-calci"):
        r = call(client, path, {"F": "1/(1+x**2)", "lowerLimit": 0,
                                "upperLimit": 1, "subIntervals": 6})
        assert r.get_json() == pytest.approx(math.pi / 4, abs=1e-4)


def test_runge_kutta_single_step(client):
    r = call(client, "/runge-kutta", {"f": "x + y", "x0": 0, "y0": 1, "h": 0.1})
    *_, x1, y1 = r.get_json()
    assert x1 == pytest.approx(0.1)
    assert y1 == pytest.approx(1.110342, abs=1e-5)  # exact: 2e^0.1 - 1.1


def test_euler_steps(client):
    r = call(client, "/euler", {"function": "x+y", "X0": 0, "Y0": 1, "H": 0.1, "N": 1})
    assert r.get_json()[0] == [0.1, 1.1]


def test_newton_raphson_finds_root(client):
    r = call(client, "/newton-raphson-calci",
             {"nrFunction": "x**3 - 2*x - 5", "initApproximation": 2, "iterations": 5})
    assert r.get_json()[-1][1] == pytest.approx(2.0945515, abs=1e-6)


def test_regula_falsi_converges(client):
    r = call(client, "/regula-falsi-calci",
             {"rfFunction": "x**3 - 2*x - 5", "rfA": 2, "rfB": 3, "iterations": 20})
    assert r.get_json()[-1][1] == pytest.approx(2.0945515, abs=1e-4)


def test_lagrange_exact_for_polynomial(client):
    # points from y = x^3 - x + 2 ... fitted exactly by a cubic
    xs = [0, 1, 2, 5]
    ys = [x**3 - x + 2 for x in xs]
    r = call(client, "/lagrange-calci", {"n": 4, "x": xs, "y": ys, "a": 3})
    assert r.get_json()[1] == pytest.approx(26)


def test_interpolation_exact_for_cubic(client):
    r = call(client, "/interpolation-solver",
             {"numDataPts": 4, "x": [1, 2, 3, 4], "y": [[1], [8], [27], [64]], "ptInter": 2.5})
    assert r.get_json()[1] == pytest.approx(15.625)


def test_caret_is_power(client):
    r = call(client, "/trapezoidal-rule-calci",
             {"F": "x^2", "lowerLimit": 0, "upperLimit": 3, "subIntervals": 300})
    assert r.get_json() == pytest.approx(9, abs=1e-3)


EVIL = [
    "__import__('os').system('id')",
    "().__class__.__bases__[0].__subclasses__()",
    "open('/etc/passwd').read()",
    "x.__class__",
    "lambda: 1",
    "[c for c in 'ab']",
    "'a' * 10",
    "exec('1')",
    "x if True else 0",
]


@pytest.mark.parametrize("expr", EVIL)
def test_code_injection_rejected(client, expr):
    r = call(client, "/trapezoidal-rule-calci",
             {"F": expr, "lowerLimit": 0, "upperLimit": 1, "subIntervals": 4})
    assert r.status_code == 400
    assert "error" in r.get_json()


def test_huge_power_does_not_hang(client):
    start = time.time()
    r = call(client, "/trapezoidal-rule-calci",
             {"F": "9**9**9**9", "lowerLimit": 0, "upperLimit": 1, "subIntervals": 4})
    assert time.time() - start < 5
    assert r.status_code == 400


@pytest.mark.parametrize("path,data", [
    ("/euler", {"function": "x+y", "X0": "abc", "Y0": 1, "H": 0.1, "N": 3}),
    ("/euler", {"function": "x+y", "X0": 0, "Y0": 1, "H": 0.1, "N": 10**9}),
    ("/euler", {"function": "1/0", "X0": 0, "Y0": 1, "H": 0.1, "N": 3}),
    ("/euler", {"function": "", "X0": 0, "Y0": 1, "H": 0.1, "N": 3}),
    ("/lagrange-calci", {"n": 3, "x": [1, 1, 2], "y": [1, 2, 3], "a": 1.5}),
    ("/regula-falsi-calci", {"rfFunction": "5", "rfA": 0, "rfB": 1, "iterations": 3}),
    ("/newton-raphson-calci", {"nrFunction": "5", "initApproximation": 1, "iterations": 3}),
])
def test_bad_input_returns_400(client, path, data):
    assert call(client, path, data).status_code == 400


def test_non_json_body_returns_400(client):
    r = client.post("/euler", data="nope", content_type="text/plain")
    assert r.status_code == 400


def test_gpa_page_loads_calculator_scripts(client):
    html = client.get("/gpa-calculators").get_data(as_text=True)
    assert "js/vtu-grading.js" in html and "js/gpa-calci.js" in html
    for year in ("2015", "2017", "2018", "2021", "2022", "2025"):
        assert f'<option value="{year}"' in html


def test_grading_rules_js():
    """The grading rules are plain JS; run their tests under node when present."""
    import shutil
    import subprocess
    node = shutil.which("node")
    if node is None:
        pytest.skip("node is not installed")
    r = subprocess.run([node, "tests/test_grading.js"], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


# ------------------------------------------------------- syllabus calculators

import toolkit  # noqa: E402


def tool(client, slug, **data):
    return client.post(f"/api/tools/{slug}", json=data)


def summary(resp):
    assert resp.status_code == 200, resp.get_json()
    return dict(resp.get_json()["summary"])


def test_every_tool_example_runs_and_page_renders(client):
    assert len(toolkit.TOOLS) >= 30
    for slug, t in toolkit.TOOLS.items():
        assert tool(client, slug, **t["example"]).status_code == 200, slug
        assert client.get(f"/tools/{slug}").status_code == 200, slug
    for hub in ("/sem1-math", "/sem2-math", "/physics"):
        assert client.get(hub).status_code == 200


def test_unknown_tool_is_404(client):
    assert client.get("/tools/nope").status_code == 404
    assert tool(client, "nope").status_code == 404


def test_tools_reject_code_and_junk(client):
    r = tool(client, "bisection", f="__import__('os').system('id')", a="1", b="2", n="5")
    assert r.status_code == 400
    assert tool(client, "gauss-seidel", A="1 2\n3", b="1 2", n="3").status_code == 400
    assert tool(client, "eigen", A="1 2 3\n4 5 6").status_code == 400
    assert tool(client, "bisection", f="x", a="1", b="2", n="5").status_code == 400  # no sign change
    assert tool(client, "de-broglie", particle="electron", mode="voltage", value="-5").status_code == 400
    assert tool(client, "eigen", A="9" * 3000).status_code == 400


def test_math_known_answers(client):
    s = summary(tool(client, "bisection", f="x**3-x-1", a="1", b="2", n="30"))
    assert abs(float(s["Root ≈"].replace("−", "-")) - 1.324718) < 1e-5
    s = summary(tool(client, "lu-decomposition", A="2 1 1\n4 3 3\n8 7 9", b="4 10 24"))
    assert [s[f"x{i} ="] for i in (1, 2, 3)] == ["1", "1", "1"]
    s = summary(tool(client, "rank-echelon", A="1 2 3\n2 4 6\n1 0 1"))
    assert s["Rank"] == "2"
    s = summary(tool(client, "gauss-elimination", A="2 1 -1\n-3 -1 2\n-2 1 2", b="8 -11 -3", method="jordan"))
    assert (s["x1 ="], s["x2 ="], s["x3 ="]) == ("2", "3", "−1")
    s = summary(tool(client, "gauss-elimination", A="1 1\n2 2", b="1 3", method="gauss"))
    assert s["Result"].startswith("Inconsistent")
    s = summary(tool(client, "gauss-elimination", A="1 1\n2 2", b="1 2", method="gauss"))
    assert s["Result"].startswith("Infinitely many")
    s = summary(tool(client, "newton-forward", x="1 2 3 4 5", y="1 8 27 64 125", p="2.5"))
    assert s["y ≈"] == "15.625"
    s = summary(tool(client, "newton-backward", x="1 2 3 4 5", y="1 8 27 64 125", p="4.5"))
    assert s["y ≈"] == "91.125"
    s = summary(tool(client, "newton-divided-difference", x="0 1 2 4", y="1 3 7 31", p="3"))
    assert abs(float(s["y ≈"]) - 15.5) < 1e-9
    s = summary(tool(client, "weddle", f="1/(1+x**2)", a="0", b="1", n="6"))
    assert abs(float(s["Integral ≈"]) - 0.785398) < 1e-3
    s = summary(tool(client, "taylor-ode", f="x+y", x0="0", y0="1", xt="0.2", order="4", steps="1"))
    assert abs(float(s["y(0.2) ≈"]) - 1.2428) < 1e-4
    s = summary(tool(client, "eigen", A="2 0 0\n0 3 4\n0 4 9"))
    assert (s["λ1"], s["λ2"], s["λ3"]) == ("11", "2", "1")
    s = summary(tool(client, "jacobian", vars="xy", exprs="x*cos(y)\nx*sin(y)"))
    assert s["J ="] == "x"
    r = tool(client, "maxima-minima", f="x**3 + y**3 - 3*x*y").get_json()
    kinds = sorted(row[-1] for row in r["tables"][0]["rows"])
    assert kinds == ["Minimum", "Saddle point (neither max nor min)"]
    s = summary(tool(client, "vector-calculus", op="div", e1="x**2", e2="y**2", e3="z**2"))
    assert s["∇·F"] == "2*x + 2*y + 2*z"
    s = summary(tool(client, "series-expansion", f="exp(x)", a="0", n="3"))
    assert s["Series"] == "x^3/6 + x^2/2 + x + 1"
    s = summary(tool(client, "power-method", A="2 0\n0 1", x0="1 1", n="30"))
    assert abs(float(s["Dominant eigenvalue ≈"]) - 2) < 1e-6


def test_physics_known_answers(client):
    s = summary(tool(client, "de-broglie", particle="electron", mode="voltage", value="150"))
    assert abs(float(s["λ (Å)"]) - 1.0014) < 1e-3          # 12.26/sqrt(150)
    s = summary(tool(client, "fermi-energy", n="8.49e28"))
    assert abs(float(s["E_F (eV)"]) - 7.04) < 0.02          # copper
    s = summary(tool(client, "fermi-factor", E="7", EF="7", T="300"))
    assert s["f(E)"] == "0.5"
    s = summary(tool(client, "optical-fibre", n1="1.5", n2="1.45", n0="1", a="25", lam="850"))
    assert abs(float(s["Numerical aperture NA"]) - 0.38406) < 1e-4
    s = summary(tool(client, "sabine-reverberation", V="2000", S="200 0.03\n150 0.60\n300 0.15"))
    assert abs(float(s["Reverberation time T (s)"]) - 2.2837) < 1e-3
    s = summary(tool(client, "springs", k="200 300", how="series", m="0.5"))
    assert s["Equivalent k (N/m)"] == "120"
    s = summary(tool(client, "two-qubit-gates", start="00", circuit="H0 CNOT01"))
    assert s["P(|00⟩)"] == "0.5" and s["P(|11⟩)"] == "0.5" and s["Entangled"].startswith("Yes")
    s = summary(tool(client, "qubit-gates", a="1", b="0", gates="H"))
    assert s["P(measure 0)"] == "0.5"
    r = tool(client, "particle-in-box", particle="electron", L="1", n="3").get_json()
    e = [float(row[2]) for row in r["tables"][0]["rows"]]
    assert abs(e[0] - 0.3764) < 1e-3 and abs(e[1] / e[0] - 4) < 1e-6 and abs(e[2] / e[0] - 9) < 1e-6
    assert tool(client, "superconductor", Hc0="6.5e4", Tc="7.2", T="8", r="1").status_code == 400
