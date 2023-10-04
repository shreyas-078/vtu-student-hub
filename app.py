# Imports
from flask import Flask, render_template, jsonify, request  # Web Server
from sympy import symbols, diff, exp  # Math eval
from numpy import array, zeros  # Math eval
import math


# Initaiate Flask Application
app = Flask(__name__, static_url_path="/static", static_folder="static")


# Route to solve Milne Predictor - Corrector method
@app.route("/milne-pc", methods=["POST"])
def milne_pc():
    func = lambda x, y: x**2 + y**2
    x = [0, 0.1, 0.2, 0.3]
    y = [1, 1.1113, 1.2507, 1.426]
    h = 0.1
    f = []

    for i in range(4):
        f.append(func(x[i], y[i]))
        print(f"x{i}-%.4f\ty{i}-%.4f\tf{i}=%0.4f" % (x[i], y[i], f[i]))

    # Predict y4 = y(x4)
    x4 = x[3] + h
    y4p = y[0] + (4 * h / 3) * (2 * f[1] - f[2] + 2 * f[3])
    predictor = 1
    print("\n The predicted value at x4 = %.4f is y4(p) = %.5f\n" % (x4, y4p))

    # Correction
    for i in range(3):
        f4p = func(x4, y4p)
        y4c = y[2] + (h / 3) * (f[2] + 4 * f[3] + f4p)
        y4p = predictor
        print(f"The corrected value at x4-%.4f in iteration {i+1} is -%.5f" % (x4, y4c))


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
    def f(x, y):
        return x + y  # INPUT FUNCTION

    x0 = float(input("Enter x0="))
    y0 = float(input("Enter y0="))
    h = float(input("Enter h="))
    n = int(input("Enter n="))

    for i in range(n + 1):
        y1 = y0 + h * f(x0, y0)
        x0 = x0 + h
        y0 = y1
        print("The value of y at x", round(x0, 2), "is=", round(y0, 4))

    def f(x):
        return -1 - x + math.exp(x)

    print("exact solution at one=", round(f(1), 4))


# Modified Euler
@app.route("/mod-euler", methods=["POST"])
def mod_euler():
    f = lambda x, y: x + y  # INPUT FUNCTION
    x0 = float(input("Enter x0 value"))
    y0 = float(input("Enter y0 value"))
    h = float(input("Enter h value"))
    n = int(input("Enter the maximum number iterations needs to be performed: "))
    x1 = x0 + h
    y1E = y0 + h * f(x0, y0)
    print("\n Initial guess by Euler's method is x-%0.2f y=%0.4f" % (x1, y1E))
    print("By Modified Euler's Method")
    print(f"Iteration\t \ty1({x1})")
    for i in range(n):
        y1 = y0 + (h / 2) * (f(x0, y0) + f(x1, y1E))
        print(i + 1, "\t\t\t%.4f" % y1)
        if abs(y1 - y1E) < 0.0001:
            break
        else:
            y1E = y1
    print(f"\n y({x1})=%.4f " % y1)


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


# Start the flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
