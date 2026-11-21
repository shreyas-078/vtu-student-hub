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
