# Imports
from flask import Flask, render_template
from sympy import symbols, diff, exp
from numpy import array, zeros


# Taylor Series
# def taylor(deriv, x, y, xStop, h):
#     X = []
#     Y = []
#     X.append(x)
#     Y.append(y)
#     while x < xStop:  # Loop over integration steps
#         D = deriv(x, y, 4)  # Derivatives of y
#         H = 1.0
#         for j in range(3):  # Build Taylor series
#             H = H * h / (j + 1)
#             y = y + D[j] * H  # H = h^j/j!
#         x = x + h
#         X.append(x)  # Append results to
#         Y.append(y)  # lists X and Y

#     return array(X), array(Y)  # Convert lists into arrays


# # Define a symbolic variable for x
# x_symbolic = symbols("x")


# # Define your deriv function
# def deriv(x, y, n):
#     D = zeros((n, 1))

#     D[0] = [2 * y[0] + 3 * exp(x)]

#     for i in range(1, n):
#         D[i] = [diff(D[i - 1], x_symbolic)]
#     return D


# x = 0.0  # Initial value of x
# xStop = 0.3  # last value
# y = array([0.0])  # Initial values of y
# h = 0.1  # Step size
# X, Y = taylor(deriv, x, y, xStop, h)
# print(
#     "The required values are :at x= %0.2f , y=%0.5f , x=%0.2f , y=%0.5f , x = %0.2f , y=%0.5f ,x = %0.2f , y=%0.5f"
#     % (X[0], Y[0], X[1], Y[1], X[2], Y[2], X[3], Y[3])
# )


# program to solve by Modified Euler's method: y'-x+y, y(0)=1,atx=0.1.
# f-lambda X,y:xty
# x0=0
# y0-1
# h=0.1
# n=int(input("Enter the maximum number iterations needs to be performed: "))
# x1-x0+h
# y1E=y@+h"f(xe,y0)
# print("InInitial guess by Euler's method is x-%0.2f y=%0.4f"%(x1,y1E))
# print("By Modified Euler's Method")
# print(f"Iteration\t\ty1((x1))")
# for i in range(n):
# y1-y@+(h/2)"(f(x0,y0)+f(x1,y1E))
# print(i+1,"It\t\t%.4f"%y1)
# if abs(y1-y1E)<0.0001:
# break
# else:
# y1E=y1
# print(f"Iny((x1))=%.4f"%y1)


# Milne predictor and corrector method
func = lambda x, y: x**2 + y**2
x = [0, 0.1, 0.2, 0.3]
y = [1, 1.1113, 1.2507, 1.426]
h = 0.1
f = []
for i in range(4):
    f.append(func(x[i], y[i]))
    print(f"x{i}-%.4f\ty{i}-%.4f\tf{i}=%0.4f" % (x[i], y[i], f[i]))
# predict y4=y(x4)
x4 = x[3] + h
y4p = y[0] + (4 * h / 3) * (2 * f[1] - f[2] + 2 * f[3])
predictor = 1
print("\n The predicted value at x4 = %.4f is y4p=%.5f\n" % (x4, y4p))
# correction
for i in range(3):
    f4p = func(x4, y4p)
    y4c = y[2] + (h / 3) * (f[2] + 4 * f[3] + f4p)
    y4p = predictor
    print(
        f"The corrected value at x4-%.4f in iteration {i+1} is y4cfi+1)-%.5f"
        % (x4, y4c)
    )


# Runge Kutta method
f = lambda x, y: 1 + y / x
x0 = (float, input("Enter x0"))
y0 = (float, input("Enter Value of y0"))
h = float(input("Enter Value of h"))
x1 = x0 + h
k1 = h * f(x0, y0)
k2 = h * f(x0 + h / 2, y0 + k1 / 2)
k3 = h * f(x0 + h / 2, y0 + k2 / 2)
k4 = h * f(x0 + h, y0 + k3)
y1 = y0 + (1 / 6) * (k1 + 2 * k2 + 2 * k3 + k4)
print(" k1=", k1)
print(" k2=", k2)
print(" k3=", k3)
print(" k4=", k4)

print(" y(%0.2f)=%.4f" % (x1, y1))


# Initaiate Flask Application
app = Flask(__name__, static_url_path="/static", static_folder="static")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/problem-solvers")
def problem_solvers():
    return render_template("problem-solvers.html")


# Start the flask app
"""if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)"""
