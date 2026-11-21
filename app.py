import re
from functools import wraps

from flask import Flask, abort, jsonify, render_template, request

import solvers
import tools_math  # noqa: F401  (registers the calculators)
import tools_physics  # noqa: F401
import toolkit
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

NAV_SECTIONS = {
    "/": "home",
    "/about-us": "about",
    "/gpa-calculators": "gpa",
    "/resources": "resources",
}


@app.context_processor
def inject_nav_section():
    """Tell the shared nav which top-level link is the current page."""
    return {"nav_section": NAV_SECTIONS.get(request.path, "solvers"),
            "tools_for": toolkit.tools_for}


HUBS = {
    "sem1-math": ("1st semester maths", "Calculus and Linear Algebra", "/sem1-math"),
    "sem2-math": ("2nd semester maths", "Numerical Methods", "/sem2-math"),
    "physics": ("Physics", "Quantum Physics and Applications", "/physics"),
}


CLASSIC = [  # (slug page, title, hub, module, summary)
    ("/newton-raphson-template", "Newton-Raphson method", "sem2-math", "1", "Root of f(x) = 0 using the derivative."),
    ("/regula-falsi-template", "Regula-Falsi method", "sem2-math", "1", "Root of f(x) = 0 by false position."),
    ("/interpolation-template", "Newton's divided difference (table form)", "sem2-math", "3", "Interpolate from a table of points."),
    ("/lagrange-template", "Lagrange interpolation", "sem2-math", "3", "Polynomial through given points, with the working."),
    ("/trapezoidal-template", "Trapezoidal rule", "sem2-math", "5", "Numerical integration by trapezoids."),
    ("/simpson-1-3-template", "Simpson's 1/3 rule", "sem2-math", "5", "Numerical integration with parabolic arcs."),
    ("/simpson-3-8-template", "Simpson's 3/8 rule", "sem2-math", "5", "Numerical integration with cubic arcs."),
    ("/euler-template", "Euler's method", "sem2-math", "5", "Step-by-step solution of y' = f(x, y)."),
    ("/mod-euler-template", "Modified Euler's method", "sem2-math", "5", "Euler with a corrector step."),
    ("/runge-kutta-template", "Runge-Kutta method", "sem2-math", "5", "Fourth-order solution of y' = f(x, y)."),
    ("/milne-pc-template", "Milne's predictor-corrector", "sem2-math", "5", "Multi-step ODE method."),
]

MODULES = {
    "sem1-math": {"1": "Multivariable calculus and series", "2": "Vector calculus", "3": "Matrices and linear systems", "4": "Vector spaces"},
    "sem2-math": {"1": "Errors and roots of equations", "2": "Linear systems and eigenvalues", "3": "Interpolation", "5": "Integration and differential equations"},
    "physics": {"1": "Quantum mechanics", "2": "Free electrons and semiconductors", "3": "Superconductivity", "4": "Lasers and optical fibres", "5": "Quantum computing"},
}


def catalog():
    """Every calculator as one flat list: title, url, hub, module, summary, course tag."""
    items = []
    for t in toolkit.TOOLS.values():
        first = t["syllabus"][0]
        mod = re.search(r"Module (\d)", first)
        code = first.split(" (")[0]
        items.append({"title": t["title"], "url": "/tools/" + t["slug"], "hub": t["hub"],
                      "module": mod.group(1) if mod else "", "summary": t["summary"], "tag": code})
    codes = {"sem2-math": "1BMATS201"}
    for url, title, hub, mod, summ in CLASSIC:
        items.append({"title": title, "url": url, "hub": hub, "module": mod, "summary": summ, "tag": codes[hub]})
    return items


def grouped(hub):
    """[(module title, [items])] for one hub, modules in syllabus order."""
    items = [i for i in catalog() if i["hub"] == hub]
    out = []
    for m, name in MODULES[hub].items():
        rows = sorted((i for i in items if i["module"] == m), key=lambda i: i["title"])
        if rows:
            out.append(("Module %s: %s" % (m, name), rows))
    rest = [i for i in items if i["module"] not in MODULES[hub]]
    if rest:
        out.append(("Other streams", sorted(rest, key=lambda i: i["title"])))
    return out


@app.route("/problem-solvers")
def problem_solvers():
    hubs = [{"key": k, "title": v[0], "course": v[1], "url": v[2], "count": len([i for i in catalog() if i["hub"] == k]),
             "examples": [i["title"] for i in catalog() if i["hub"] == k][:4]} for k, v in HUBS.items()]
    return render_template("problem-solvers.html", hubs=hubs, groups=[(HUBS[k][0], grouped(k)) for k in HUBS],
                           total=len(catalog()))


@app.route("/tools/<slug>")
def tool_page(slug):
    t = toolkit.TOOLS.get(slug)
    if t is None:
        abort(404)
    return render_template("tool.html", tool=toolkit.public_spec(t), hub=HUBS[t["hub"]])


@app.route("/api/tools/<slug>", methods=["POST"])
def tool_api(slug):
    if slug not in toolkit.TOOLS:
        abort(404)

    @api
    def run(data):
        return toolkit.run_tool(slug, data)

    return run()


PAGES = {
    "/": "index.html",
    "/about-us": "about-us.html",
    "/gpa-calculators": "gpa-calculators.html",
    "/resources": "resources.html",
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


def _hub_view(hub):
    return lambda: render_template("hub.html", hub=hub, title=HUBS[hub][0], course=HUBS[hub][1], groups=grouped(hub))


for _hub, (_t, _c, _path) in HUBS.items():
    app.add_url_rule(_path, endpoint="hub_" + _hub.replace("-", "_"), view_func=_hub_view(_hub))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
