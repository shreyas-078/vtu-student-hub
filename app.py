from functools import wraps

from flask import Flask, jsonify, render_template, request

import solvers
from solvers import InputError, number_list, to_float, to_int

app = Flask(__name__, static_url_path="/static", static_folder="static")


def api(handler):
    """Wrap a solver route: parse JSON, turn bad input into a 400 response."""

    @wraps(handler)
    def wrapper():
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({"error": "Request body must be JSON"}), 400
        try:
            return jsonify(handler(data))
        except InputError as exc:
            return jsonify({"error": str(exc)}), 400

    return wrapper


def post(path, endpoint=None):
    def register(handler):
        name = endpoint or handler.__name__
        return app.route(path, methods=["POST"], endpoint=name)(api(handler))

    return register


# ---------------------------------------------------------------- solver API


@post("/milne-pc")
def milne_pc(d):
    xs = number_list([d.get(f"x{i}") for i in range(4)], "x", 4)
    ys = number_list([d.get(f"y{i}") for i in range(4)], "y", 4)
    return solvers.milne_pc(d.get("f"), xs, ys)


@post("/runge-kutta")
def runge_kutta(d):
    return solvers.runge_kutta(
        d.get("f"), to_float(d.get("x0"), "x0"), to_float(d.get("y0"), "y0"),
        to_float(d.get("h"), "h"),
    )


@post("/euler")
def euler(d):
    return solvers.euler(
        d.get("function"), to_float(d.get("X0"), "X0"), to_float(d.get("Y0"), "Y0"),
        to_float(d.get("H"), "H"), to_int(d.get("N"), "N", minimum=0),
    )


@post("/mod-euler")
def mod_euler(d):
    return solvers.mod_euler(
        d.get("F"), to_float(d.get("X0"), "X0"), to_float(d.get("Y0"), "Y0"),
        to_float(d.get("H"), "H"), to_int(d.get("N"), "N", minimum=0),
    )


@post("/interpolation-solver")
def interpolation_solver(d):
    n = to_int(d.get("numDataPts"), "numDataPts", minimum=2, maximum=50)
    xs = number_list(d.get("x"), "x", n)
    raw_y = d.get("y")
    if not isinstance(raw_y, list) or len(raw_y) < n:
        raise InputError(f"'y' needs {n} values")
    ys = [
        to_float(row[0] if isinstance(row, list) and row else row, "y")
        for row in raw_y[:n]
    ]
    return solvers.interpolation(n, xs, ys, to_float(d.get("ptInter"), "ptInter"))


@post("/newton-raphson-calci")
def newton_raphson(d):
    return solvers.newton_raphson(
        d.get("nrFunction"), to_float(d.get("initApproximation"), "initApproximation"),
        to_int(d.get("iterations"), "iterations"),
    )


@post("/regula-falsi-calci")
def regula_falsi(d):
    return solvers.regula_falsi(
        d.get("rfFunction"), to_float(d.get("rfA"), "rfA"), to_float(d.get("rfB"), "rfB"),
        to_int(d.get("iterations"), "iterations"),
    )


def _quadrature(method):
    def handler(d):
        return method(
            d.get("F"), to_float(d.get("lowerLimit"), "lowerLimit"),
            to_float(d.get("upperLimit"), "upperLimit"),
            to_int(d.get("subIntervals"), "subIntervals"),
        )

    return handler


post("/trapezoidal-rule-calci", "trapezoidal")(_quadrature(solvers.trapezoidal))
post("/simpson-1-3-calci", "simpson_1_3")(_quadrature(solvers.simpson_1_3))
post("/simpson-3-8-calci", "simpson_3_8")(_quadrature(solvers.simpson_3_8))


@post("/lagrange-calci")
def lagrange(d):
    n = to_int(d.get("n"), "n", minimum=1, maximum=50)
    return solvers.lagrange(
        n, number_list(d.get("x"), "x", n), number_list(d.get("y"), "y", n),
        to_float(d.get("a"), "a"),
    )


# --------------------------------------------------------------------- pages

PAGES = {
    "/": "index.html",
    "/about-us": "about-us.html",
    "/problem-solvers": "problem-solvers.html",
    "/gpa-calculators": "gpa-calculators.html",
    "/resources": "resources.html",
    "/sem1-math": "subjects/math/sem1-math.html",
    "/sem2-math": "subjects/math/sem2-math.html",
    "/physics": "subjects/physics/physics.html",
    "/runge-kutta-template": "subjects/math/runge-kutta.html",
    "/milne-pc-template": "subjects/math/milne-pc.html",
    "/euler-template": "subjects/math/euler.html",
    "/mod-euler-template": "subjects/math/mod-euler.html",
    "/newton-raphson-template": "subjects/math/newton-raphson.html",
    "/regula-falsi-template": "subjects/math/regula-falsi.html",
    "/interpolation-template": "subjects/math/interpolation.html",
    "/trapezoidal-template": "subjects/math/trapezoidal-rule.html",
    "/simpson-1-3-template": "subjects/math/simpson-1-3.html",
    "/simpson-3-8-template": "subjects/math/simpson-3-8.html",
    "/lagrange-template": "subjects/math/lagrange.html",
}

for _path, _template in PAGES.items():
    app.add_url_rule(
        _path,
        endpoint="page_" + (_path.strip("/").replace("-", "_") or "index"),
        view_func=(lambda t=_template: render_template(t)),
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
