# Imports
from flask import Flask, render_template, jsonify, request  # Web Server
from sympy import symbols, diff, exp, lambdify, pprint, simplify  # Math eval
from numpy import array, zeros  # Math eval
import math  # More Math Eval


# Initaiate Flask Application
app = Flask(__name__, static_url_path="/static", static_folder="static")


# Route to solve Milne Predictor - Corrector method
@app.route("/milne-pc", methods=["POST"])
def milne_pc():
    answer = []
    data = request.get_json()
    func_exp = data.get("f")
    func = lambda x, y: eval(func_exp)  # SERVER BREAKER, FIX BY ADDING REGEX IN JS
    x = [
        float(data.get("x0")),
        float(data.get("x1")),
        float(data.get("x2")),
        float(data.get("x3")),
    ]
    y = [
        float(data.get("y0")),
        float(data.get("y1")),
        float(data.get("y2")),
        float(data.get("y3")),
    ]
    h = x[1] - x[0]
    f = []

    for i in range(4):
        f.append(func(x[i], y[i]))

    # Predict y4 = y(x4)
    x4 = x[3] + h
    y4p = y[0] + (4 * h / 3) * (2 * f[1] - f[2] + 2 * f[3])
    # predictor = 1
    answer.append(y4p)
    # Correction
    for i in range(1, 4):
        f4p = func(x4, y4p)
        y4c = y[2] + (h / 3) * (f[2] + 4 * f[3] + f4p)
        y4p = y4c
        answer.append(y4c)

    return jsonify(answer)


# Runge Kutta method solver route
@app.route("/runge-kutta", methods=["POST"])
def runge_kutta():
    data = request.get_json()
    func = data.get("f")
    x0 = float(data.get("x0"))
    f = lambda x, y: eval(
        func
    )  # IMPORTANT: ADD REGEX FOR FUNC SO AS TO AVOID SERVER NUKING COMMANDS
    y0 = float(data.get("y0"))
    h = float(data.get("h"))
    x1 = x0 + h
    k1 = h * f(x0, y0)
    k2 = h * f(x0 + h / 2, y0 + k1 / 2)
    k3 = h * f(x0 + h / 2, y0 + k2 / 2)
    k4 = h * f(x0 + h, y0 + k3)
    y1 = y0 + (1 / 6) * (k1 + 2 * k2 + 2 * k3 + k4)
    return jsonify([k1, k2, k3, k4, x1, y1])


# Euler method
@app.route("/euler", methods=["POST"])
def euler():
    data = request.get_json()
    func = data.get("function")

    ans = []

    def f(x, y):
        return eval(func)  # INPUT FUNCTION ADD REGEX

    x0 = float(data.get("X0"))
    y0 = float(data.get("Y0"))
    h = float(data.get("H"))
    n = int(data.get("N"))

    for i in range(n + 1):
        y1 = y0 + h * f(x0, y0)
        x0 = x0 + h
        y0 = y1
        ans.append((round(x0, 2), round(y0, 4)))

    return jsonify(ans)


# Modified Euler
@app.route("/mod-euler", methods=["POST"])
def mod_euler():
    data = request.get_json()
    func = data.get("F")

    f = lambda x, y: eval(func)  # INPUT FUNCTION ADD REGEX
    x0 = float(data.get("X0"))
    y0 = float(data.get("Y0"))
    h = float(data.get("H"))
    n = int(data.get("N"))
    x1 = x0 + h
    y1E = y0 + h * f(x0, y0)

    print("\n Initial guess by Euler's method is x-%0.2f y=%0.4f" % (x1, y1E))

    print(f"Iteration\t \ty1({x1})")
    for i in range(n):
        y1 = y0 + (h / 2) * (f(x0, y0) + f(x1, y1E))
        print(i + 1, "\t\t\t%.4f" % y1)
        if abs(y1 - y1E) < 0.0001:
            break
        else:
            y1E = y1

    print(f"\n y({x1})=%.4f " % y1)


# INTERPOLATION
@app.route("/interpolation-solver")
def interpolation_solver():
    n = int(input("Enter number of data points : "))
    x = zeros((n))
    y = zeros((n, n))
    # Reading data points
    print("Enter data for x and y: ")
    for i in range(n):
        x[i] = float(input("x[" + str(i) + "]= "))
        y[i][0] = float(input("y[" + str(i) + "]= "))
    # Generating forward difference table
    for i in range(1, n):
        for j in range(0, n - i):
            y[j][i] = y[j + 1][i - 1] - y[j][i - 1]

    print("\ nFORWARD DIFFERENCE TABLE \n")

    for i in range(0, n):
        print("%0.2f " % (x[i]), end="")
        for j in range(0, n - i):
            print("\t\t%0.2f " % (y[i][j]), end="")
        print()
    # obtaining the polynomial

    t = symbols("t")
    f = []

    p = (t - x[0]) / (x[1] - x[0])
    f.append(p)
    for i in range(1, n - 1):
        f.append(f[i - 1] * (p - i) / (i + 1))
        poly = y[0][0]
    for i in range(n - 1):
        poly = poly + y[0][i + 1] * f[i]
    simp_poly = simplify(poly)
    print("\ nTHE INTERPOLATING POLYNOMIAL IS\n")
    pprint(simp_poly)
    # if you want to interpolate at some point the next session will help
    inter = input("Do you want to interpolate at a point (y/n)? ")  # y
    if inter == "y":
        a = float(input("enter the point "))  # 2
        interpol = lambdify(t, simp_poly)
        result = interpol(a)
        print("\ nThe value of the function at ", a, "is\n", result)


# Home Route for Homepage
@app.route("/")
def home():
    return render_template("index.html")


# Route to show about us page
@app.route("/about-us")
def about_us():
    return render_template("about-us.html")


# Route to redirect to problem solvers page
@app.route("/problem-solvers")
def problem_solvers():
    return render_template("problem-solvers.html")


@app.route("/gpa-calculators")
def gpa_calculators():
    return render_template("gpa-calculators.html")


# Route to redirect to math problem solvers page
@app.route("/math")
def math_page():
    return render_template("subjects/math/math.html")


# Route to redirect to runge-kutta solver page
@app.route("/runge-kutta-template")
def runge_kutta_home():
    return render_template("subjects/math/runge-kutta.html")


# Route to redirect to Milne's Predictor Corrector Method Page
@app.route("/milne-pc-template")
def milne_pc_page():
    return render_template("subjects/math/milne-pc.html")


@app.route("/euler-template")
def euler_template_page():
    return render_template("subjects/math/euler.html")


@app.route("/mod-euler-template")
def euler_template_page():
    return render_template("subjects/math/mod-euler.html")


@app.route("/physics")
def physics():
    return render_template("subjects/physics/physics.html")


# Start the flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
