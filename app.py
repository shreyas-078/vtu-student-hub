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

    init_guess = (x1, y1E)
    ans_iterations = []

    for i in range(n):
        y1 = y0 + (h / 2) * (f(x0, y0) + f(x1, y1E))
        ans_iterations.append(y1)
        if abs(y1 - y1E) < 0.0001:
            break
        else:
            y1E = y1

    final_y1 = y1

    return jsonify([init_guess, ans_iterations, final_y1])


# INTERPOLATION
@app.route("/interpolation-solver", methods=["POST"])
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

    print("\n FORWARD DIFFERENCE TABLE \n")

    for i in range(0, n):
        print("%0.2f " % (x[i]), end="")
        for j in range(0, n - i):
            print("\t\t%0.2f " % (y[i][j]), end="")
        print()
    # Obtaining the polynomial

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
    print("\n THE INTERPOLATING POLYNOMIAL IS \n")
    pprint(simp_poly)

    # If you want to interpolate at some point the next session will help
    inter = input("Do you want to interpolate at a point (y/n)? ")  # Y
    if inter == "y":
        a = float(input("enter the point "))  # 2
        interpol = lambdify(t, simp_poly)
        result = interpol(a)
        print("\ nThe value of the function at ", a, "is\n", result)


# NEWTON-RAPHSON
@app.route("/newton-raphson-calci", methods=["POST"])
def newton_raphson_solver():
    answer = []

    data = request.get_json()
    x = symbols("x")
    func = data.get("nrFunction")

    g = eval(func)  # ADD REGEX OR SOMETHING
    f = lambdify(x, g)
    dg = diff(g)
    df = lambdify(x, dg)

    x0 = float(data.get("initApproximation"))
    n = int(data.get("iterations"))

    for i in range(1, n + 1):
        x1 = x0 - (f(x0) / df(x0))
        answer.append((i, x1, f(x1)))
        x0 = x1

    return jsonify(answer)


# Regula Falsi calculator method
@app.route("/regula-falsi-calci", methods=["POST"])
def regula_falsi_solver():
    answer = []
    data = request.get_json()
    x = symbols("x")
    func = data.get("rfFunction")
    g = eval(func)
    f = lambdify(x, g)
    a = float(data.get("rfA"))
    b = float(data.get("rfB"))
    N = int(data.get("iterations"))
    for i in range(1, N + 1):
        c = (a * f(b) - b * f(a)) / (f(b) - f(a))
        if f(a) * f(c) < 0:
            b = c
        else:
            a = c
        answer.append((i, c, f(c)))
    return answer


# Trapezoidal Rule Method
@app.route("/trapezoidal-rule-calci", methods=["POST"])
def trapezoidal_rule_solver():
    data = request.get_json()
    func = data.get("F")

    # Definition of the function to integrate
    def my_func(x):
        return eval(func)

    # Function to implement trapezoidal method
    def trapezoidal(x0, xn, n):
        h = (xn - x0) / n  # Calculating step size

        # Finding sum
        integration = my_func(x0) + my_func(xn)  # Adding first and last terms

        for i in range(1, n):
            k = x0 + i * h  # i-th step value
            integration = integration + 2 * my_func(k)  # Adding areas of the trapezoids

        # Proportioning sum of trapezoid areas
        integration = integration * h / 2
        return integration

    # Input section
    lower_limit = float(data.get("lowerLimit"))
    upper_limit = float(data.get("upperLimit"))
    sub_interval = int(data.get("subIntervals"))

    # Call trapezoidal () method and get result
    result = trapezoidal(lower_limit, upper_limit, sub_interval)

    # return result
    return jsonify(result)


# Simpsons 1/3rd Rule
@app.route("/simpson-1-3-calci", methods=["POST"])
def simpson_1_3_rule_solver():
    data = request.get_json()
    func = data.get("F")

    # Definition of the function to integrate
    def my_func(x):
        return eval(func)

    # Function to implement the Simpson 's one - third rule
    def simpson13(x0, xn, n):
        h = (xn - x0) / n  # calculating step size
        # Finding sum
        integration = my_func(x0) + my_func(xn)
        k = x0
        for i in range(1, n):
            if i % 2 == 0:
                integration = integration + 4 * my_func(k)
            else:
                integration = integration + 2 * my_func(k)
            k += h

        # Finding final integration value
        integration = integration * h * (1 / 3)
        return integration
        # Input section

    lower_limit = float(data.get("lowerLimit"))
    upper_limit = float(data.get("upperLimit"))
    sub_intervals = int(data.get("subIntervals"))
    result = simpson13(lower_limit, upper_limit, sub_intervals)
    return jsonify(result)


# Simpsons_3_8_rule
@app.route("/simpson-3-8-calci", methods=["POST"])
def simpson_3_8_rule_solver():
    data = request.get_json()
    func = data.get("F")

    def f(some):
        return eval(func, {"x": some})

    def simpsons_3_8_rule(f, a, b, n):
        h = (b - a) / n
        s = f(a) + f(b)
        for i in range(1, n, 3):
            s += 3 * f(a + i * h)
        for i in range(3, n - 1, 3):
            s += 3 * f(a + i * h)
        for i in range(2, n - 2, 3):
            s += 2 * f(a + i * h)
        return s * 3 * h / 8

    lower_limit = float(data.get("lowerLimit"))
    upper_limit = float(data.get("upperLimit"))
    sub_intervals = int(data.get("subIntervals"))
    result = simpsons_3_8_rule(f, lower_limit, upper_limit, sub_intervals)
    return jsonify(result)


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


# Render mod
@app.route("/mod-euler-template")
def mod_euler_template_page():
    return render_template("subjects/math/mod-euler.html")


# Render the Physics homepage
@app.route("/physics")
def physics():
    return render_template("subjects/physics/physics.html")


# Render the Newton Raphson Template Page
@app.route("/newton-raphson-template")
def newton_raphson_template():
    return render_template("subjects/math/newton-raphson.html")


# Render the Regula Falsi Page
@app.route("/regula-falsi-template")
def regula_falsi_template():
    return render_template("subjects/math/regula-falsi.html")


# Render the Interpolation/Extrapolation Page
@app.route("/inter-extrapolation-template")
def inter_extrapolation_template():
    return render_template("subjects/math/inter-extrapolation.html")


# Render the divided difference page
@app.route("/dd-solver-template")
def dd_solver_template():
    return render_template("subjects/math/div-diff.html")


# Render the Trapezoidal Rule Page
@app.route("/trapezoidal-template")
def trapezoidal_template():
    return render_template("subjects/math/trapezoidal-rule.html")


# Render the Simpson's 1/3rd Rule Solver Template
@app.route("/simpson-1-3-template")
def simpson_1_3_template():
    return render_template("subjects/math/simpson-1-3.html")


# Render the Simpson's 3/8th Rule Solver Template
@app.route("/simpson-3-8-template")
def simpson_3_8_template():
    return render_template("subjects/math/simpson-3-8.html")


# Render Lagrange Interpolation Page
@app.route("/lagrange-template")
def lagrange_template():
    return render_template("subjects/math/lagrange.html")


# Start the flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
