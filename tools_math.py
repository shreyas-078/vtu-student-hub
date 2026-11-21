"""Mathematics calculators for the VTU first-year syllabus (Semester 1 and 2).

Course codes and module numbers come from the VTU 2025 scheme syllabus PDFs
(https://vtu.ac.in/en/b-e-scheme-syllabus/).
"""

import math
from fractions import Fraction

import numpy as np
import sympy
from sympy import symbols

from solvers import InputError, compile_function
from solvers import parse_expression as _parse
from toolkit import (Out, check_finite, field, g, integer, matrix, num, tool,
                     vector)

S201 = "1BMATS201 (Numerical Methods)"
S101 = "1BMATS101 (Calculus and Linear Algebra)"
X, Y, Z = symbols("x y z")


def parse_expression(text, variables):
    """Parse safely, then turn the parser's float constants back into exact rationals."""
    return sympy.nsimplify(_parse(text, variables), rational=True)


def sym(e):
    return sympy.sstr(e).replace("**", "^")


def _table_cols(n, prefix):
    return [prefix + str(i + 1) for i in range(n)]


# ============================================================ Semester 2


@tool("error-calculator", "Errors: absolute, relative, percentage", "sem2-math",
      [S201 + ", Module 1"], "Absolute, relative and percentage error between a true and an approximate value.",
      [field("true", "True value"), field("approx", "Approximate value")],
      {"true": "3.14159265", "approx": "3.1416"},
      formula="Ea = |true − approx|,  Er = Ea ÷ |true|,  Ep = Er × 100")
def error_calculator(d):
    t, a = num(d, "true", "True value"), num(d, "approx", "Approximate value")
    if t == 0:
        raise InputError("True value cannot be 0 (relative error would be undefined)")
    ea = abs(t - a)
    return (Out().add("Absolute error", ea).add("Relative error", ea / abs(t))
            .add("Percentage error", ea / abs(t) * 100))


@tool("bisection", "Bisection method", "sem2-math", [S201 + ", Module 1"],
      "Root of f(x) = 0 by repeated halving of an interval that brackets it.",
      [field("f", "f(x)", "text", help="Use x, e.g. x**3 - x - 1. Functions: sin cos tan exp log sqrt."),
       field("a", "Lower end a"), field("b", "Upper end b"),
       field("n", "Iterations", "int", "10")],
      {"f": "x**3 - x - 1", "a": "1", "b": "2", "n": "10"},
      formula="c = (a + b) ÷ 2; keep the half where f changes sign. Error after n steps ≤ (b − a) ÷ 2ⁿ")
def bisection(d):
    f = compile_function(d["f"], ("x",))
    a, b, n = num(d, "a"), num(d, "b"), integer(d, "n", "Iterations", 1, 100)
    if a >= b:
        raise InputError("a must be less than b")
    fa, fb = f(a), f(b)
    if fa * fb > 0:
        raise InputError(f"f(a) = {g(fa)} and f(b) = {g(fb)} have the same sign, so no root is guaranteed in [a, b]")
    a0, b0, rows, c = a, b, [], a
    for i in range(1, n + 1):
        c = (a + b) / 2
        fc = f(c)
        rows.append([i, a, b, c, fc])
        if fc == 0:
            break
        if fa * fc < 0:
            b = c
        else:
            a, fa = c, fc
    return (Out().add("Root ≈", c).add("f(root)", f(c))
            .add("Error bound", (b0 - a0) / 2 ** len(rows))
            .table("Iterations", ["n", "a", "b", "c = (a+b)/2", "f(c)"], rows))


@tool("secant", "Secant method", "sem2-math", [S201 + ", Module 1"],
      "Root of f(x) = 0 from two starting guesses, with no derivative needed.",
      [field("f", "f(x)", "text"), field("x0", "First guess x₀"), field("x1", "Second guess x₁"),
       field("n", "Iterations", "int", "6")],
      {"f": "x**3 - 2*x - 5", "x0": "2", "x1": "3", "n": "6"},
      formula="x₍ₙ₊₁₎ = xₙ − f(xₙ)·(xₙ − xₙ₋₁) ÷ (f(xₙ) − f(xₙ₋₁))")
def secant(d):
    f = compile_function(d["f"], ("x",))
    x0, x1, n = num(d, "x0"), num(d, "x1"), integer(d, "n", "Iterations", 1, 100)
    rows = []
    for i in range(1, n + 1):
        f0, f1 = f(x0), f(x1)
        if f1 == f0:
            if f1 == 0:
                break
            raise InputError("f(xₙ) equals f(xₙ₋₁), so the secant is flat; choose other guesses")
        x2 = x1 - f1 * (x1 - x0) / (f1 - f0)
        check_finite(x2)
        rows.append([i, x0, x1, x2, f(x2)])
        x0, x1 = x1, x2
    return (Out().add("Root ≈", x1).add("f(root)", f(x1))
            .table("Iterations", ["n", "xₙ₋₁", "xₙ", "xₙ₊₁", "f(xₙ₊₁)"], rows))


@tool("gauss-seidel", "Gauss-Seidel iteration", "sem2-math", [S201 + ", Module 2"],
      "Approximate solution of A x = b by Gauss-Seidel iteration.",
      [field("A", "Matrix A (one row per line)", "matrix", rows=3),
       field("b", "Right-hand side b", "vector"),
       field("x0", "Starting guess (blank = all zeros)", "vector", optional=True),
       field("n", "Iterations", "int", "6")],
      {"A": "10 -1 2\n-1 11 -1\n2 -1 10", "b": "6 25 -11", "x0": "", "n": "6"},
      formula="xᵢ ← (bᵢ − Σⱼ<ᵢ aᵢⱼxⱼ(new) − Σⱼ>ᵢ aᵢⱼxⱼ(old)) ÷ aᵢᵢ")
def gauss_seidel(d):
    A = matrix(d, "A", "Matrix A", square=True, max_n=8)
    n = len(A)
    b = vector(d, "b", "b", size=n)
    x = vector(d, "x0", "Starting guess", size=n) if d["x0"] else [0.0] * n
    its = integer(d, "n", "Iterations", 1, 100)
    if any(A[i][i] == 0 for i in range(n)):
        raise InputError("A diagonal entry is zero; reorder the equations so the diagonal is non-zero")
    rows = []
    for k in range(1, its + 1):
        for i in range(n):
            s = sum(A[i][j] * x[j] for j in range(n) if j != i)
            x[i] = (b[i] - s) / A[i][i]
        check_finite(*x)
        rows.append([k] + list(x))
    out = Out()
    for i in range(n):
        out.add(f"x{i + 1} ≈", x[i])
    dominant = all(abs(A[i][i]) >= sum(abs(A[i][j]) for j in range(n) if j != i) for i in range(n))
    if not dominant:
        out.note("A is not diagonally dominant, so convergence is not guaranteed. Check that the values settle.")
    return out.table("Iterations", ["n"] + _table_cols(n, "x"), rows)


@tool("lu-decomposition", "LU decomposition (Doolittle)", "sem2-math", [S201 + ", Module 2"],
      "Factor A = L U with a unit diagonal on L, and optionally solve A x = b.",
      [field("A", "Matrix A", "matrix", rows=3),
       field("b", "Right-hand side b (optional)", "vector", optional=True)],
      {"A": "2 1 1\n4 3 3\n8 7 9", "b": "4 10 24"},
      formula="uᵢⱼ = aᵢⱼ − Σₖ lᵢₖukⱼ;  lᵢⱼ = (aᵢⱼ − Σₖ lᵢₖukⱼ) ÷ uⱼⱼ;  then L y = b, U x = y")
def lu_decomposition(d):
    A = matrix(d, "A", "Matrix A", square=True, max_n=8)
    n = len(A)
    L = [[0.0] * n for _ in range(n)]
    U = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i, n):
            U[i][j] = A[i][j] - sum(L[i][k] * U[k][j] for k in range(i))
        if abs(U[i][i]) < 1e-12:
            raise InputError(f"Zero pivot at row {i + 1}: this matrix needs a row exchange, which plain Doolittle does not do")
        L[i][i] = 1.0
        for j in range(i + 1, n):
            L[j][i] = (A[j][i] - sum(L[j][k] * U[k][i] for k in range(i))) / U[i][i]
    out = (Out().table("L", _table_cols(n, "c"), L).table("U", _table_cols(n, "c"), U))
    if d["b"]:
        b = vector(d, "b", "b", size=n)
        y = [0.0] * n
        for i in range(n):
            y[i] = b[i] - sum(L[i][k] * y[k] for k in range(i))
        x = [0.0] * n
        for i in reversed(range(n)):
            x[i] = (y[i] - sum(U[i][k] * x[k] for k in range(i + 1, n))) / U[i][i]
        for i in range(n):
            out.add(f"x{i + 1} =", x[i])
        out.table("Intermediate y (from L y = b)", ["i", "yᵢ"], [[i + 1, y[i]] for i in range(n)])
    return out


@tool("power-method", "Rayleigh power method", "sem2-math", [S201 + ", Module 2"],
      "Dominant eigenvalue and eigenvector by repeated multiplication.",
      [field("A", "Matrix A", "matrix", rows=3),
       field("x0", "Starting vector (blank = all ones)", "vector", optional=True),
       field("n", "Iterations", "int", "8")],
      {"A": "6 -2 2\n-2 3 -1\n2 -1 3", "x0": "1 1 1", "n": "8"},
      formula="y = A x;  λ ≈ largest component of y;  x ← y ÷ λ.  Rayleigh quotient λ = xᵀAx ÷ xᵀx")
def power_method(d):
    A = np.array(matrix(d, "A", "Matrix A", square=True, max_n=8))
    n = len(A)
    x = np.array(vector(d, "x0", "Starting vector", size=n)) if d["x0"] else np.ones(n)
    its = integer(d, "n", "Iterations", 1, 100)
    rows = []
    for k in range(1, its + 1):
        y = A @ x
        lam = y[np.argmax(np.abs(y))]
        if lam == 0:
            raise InputError("A x = 0 for the current vector; choose another starting vector")
        x = y / lam
        check_finite(lam, *x)
        rows.append([k, float(lam)] + [float(v) for v in x])
    rq = float(x @ A @ x / (x @ x))
    actual = np.linalg.eigvals(A)
    dom = actual[np.argmax(np.abs(actual))]
    out = Out().add("Dominant eigenvalue ≈", rows[-1][1]).add("Rayleigh quotient", rq)
    out.add("Eigenvector ≈ (scaled so the largest entry is 1)", "(" + ", ".join(g(float(v)) for v in x) + ")")
    out.add("Exact dominant eigenvalue (for comparison)", g(complex(dom)))
    return out.table("Iterations", ["n", "λ"] + _table_cols(n, "x"), rows)


@tool("jacobi-eigen", "Jacobi's method (symmetric matrices)", "sem2-math", [S201 + ", Module 2"],
      "All eigenvalues and eigenvectors of a real symmetric matrix by plane rotations.",
      [field("A", "Symmetric matrix A", "matrix", rows=3)],
      {"A": "4 1 2\n1 3 0\n2 0 5"},
      formula="tan 2θ = 2aₚq ÷ (aqq − aₚₚ); rotate to zero the largest off-diagonal entry, repeat")
def jacobi_eigen(d):
    A = np.array(matrix(d, "A", "Matrix A", square=True, max_n=6))
    n = len(A)
    if not np.allclose(A, A.T):
        raise InputError("Jacobi's method needs a symmetric matrix (aᵢⱼ = aⱼᵢ)")
    V = np.eye(n)
    rows = []
    for step in range(1, 101):
        off = np.abs(A - np.diag(np.diag(A)))
        p, q = np.unravel_index(np.argmax(off), off.shape)
        if off[p, q] < 1e-10:
            break
        theta = 0.5 * math.atan2(2 * A[p, q], A[q, q] - A[p, p])
        c, s = math.cos(theta), math.sin(theta)
        R = np.eye(n)
        R[p, p] = R[q, q] = c
        R[p, q], R[q, p] = s, -s
        A = R.T @ A @ R
        V = V @ R
        rows.append([step, f"({p + 1}, {q + 1})", math.degrees(theta), float(np.max(np.abs(A - np.diag(np.diag(A)))))])
    vals = np.diag(A)
    order = np.argsort(vals)[::-1]
    out = Out()
    for k, i in enumerate(order):
        out.add(f"Eigenvalue {k + 1}", float(vals[i]))
    out.table("Eigenvectors (columns, unit length)", _table_cols(n, "v"),
              [[float(V[r][i]) for i in order] for r in range(n)])
    out.table("Rotations", ["step", "(p, q)", "θ (degrees)", "largest off-diagonal left"], rows)
    return out


@tool("norms-condition", "Norms and condition number", "sem2-math", [S201 + ", Module 2"],
      "Vector and matrix norms (L1, L2, L∞) and the condition number of a matrix.",
      [field("A", "Matrix A (square)", "matrix", rows=3),
       field("v", "Vector v (optional)", "vector", optional=True)],
      {"A": "1 2\n3 4", "v": "3 -4 12"},
      formula="‖A‖₁ = max column sum, ‖A‖∞ = max row sum, ‖A‖₂ = largest singular value; κ(A) = ‖A‖·‖A⁻¹‖")
def norms_condition(d):
    A = np.array(matrix(d, "A", "Matrix A", square=True, max_n=8))
    out = Out()
    if d["v"]:
        v = np.array(vector(d, "v", "Vector v"))
        out.add("‖v‖₁", float(np.sum(np.abs(v)))).add("‖v‖₂", float(np.linalg.norm(v))).add("‖v‖∞", float(np.max(np.abs(v))))
    out.add("‖A‖₁ (max column sum)", float(np.linalg.norm(A, 1)))
    out.add("‖A‖∞ (max row sum)", float(np.linalg.norm(A, np.inf)))
    out.add("‖A‖₂ (spectral)", float(np.linalg.norm(A, 2)))
    out.add("‖A‖F (Frobenius)", float(np.linalg.norm(A, "fro")))
    if abs(np.linalg.det(A)) < 1e-12:
        out.note("A is singular, so the condition number is infinite.")
    else:
        for label, p in (("L1", 1), ("L2", 2), ("L∞", np.inf)):
            out.add(f"κ(A) in {label} norm", float(np.linalg.cond(A, p)))
        out.note("A condition number far above 1 means the system is ill-conditioned: small changes in the data can change the solution a lot.")
    return out


def _equal_spaced(xs):
    h = xs[1] - xs[0]
    if h == 0 or any(abs((xs[i + 1] - xs[i]) - h) > 1e-9 * max(1.0, abs(h)) for i in range(len(xs) - 1)):
        raise InputError("The x values must be equally spaced and increasing for this method")
    return h


def _diff_table(ys):
    cols = [list(ys)]
    while len(cols[-1]) > 1:
        c = cols[-1]
        cols.append([c[i + 1] - c[i] for i in range(len(c) - 1)])
    return cols


def _xy(d):
    xs = vector(d, "x", "x values", minimum=2, maximum=12)
    ys = vector(d, "y", "y values", size=len(xs))
    return xs, ys


@tool("newton-forward", "Newton-Gregory forward interpolation", "sem2-math", [S201 + ", Module 3"],
      "Interpolate near the start of an equally spaced table.",
      [field("x", "x values", "vector", help="equally spaced, increasing"), field("y", "y values", "vector"),
       field("p", "Find y at x =")],
      {"x": "1 2 3 4 5", "y": "1 8 27 64 125", "p": "2.5"},
      formula="y = y₀ + pΔy₀ + p(p−1)/2!·Δ²y₀ + p(p−1)(p−2)/3!·Δ³y₀ + …,  p = (x − x₀) ÷ h")
def newton_forward(d):
    xs, ys = _xy(d)
    h, pt = _equal_spaced(xs), num(d, "p", "x")
    cols = _diff_table(ys)
    p = (pt - xs[0]) / h
    total, term, rows = ys[0], 1.0, [["y₀", ys[0]]]
    for k in range(1, len(cols)):
        term *= (p - (k - 1)) / k
        total += term * cols[k][0]
        rows.append([f"Δ{k}y₀ term", term * cols[k][0]])
    out = Out().add("h", h).add("p", p).add("y ≈", total)
    if not (xs[0] <= pt <= xs[-1]):
        out.note("x lies outside the table, so this is extrapolation and may be inaccurate.")
    elif p > 0.5 * (len(xs) - 1):
        out.note("x is in the second half of the table, where the backward formula is the better choice.")
    out.table("Difference table", ["x", "y"] + [f"Δ{k}" for k in range(1, len(cols))],
              [[xs[i]] + [cols[k][i] if i < len(cols[k]) else "" for k in range(len(cols))] for i in range(len(xs))])
    return out.table("Terms added", ["term", "value"], rows)


@tool("newton-backward", "Newton-Gregory backward interpolation", "sem2-math", [S201 + ", Module 3"],
      "Interpolate near the end of an equally spaced table.",
      [field("x", "x values", "vector", help="equally spaced, increasing"), field("y", "y values", "vector"),
       field("p", "Find y at x =")],
      {"x": "1 2 3 4 5", "y": "1 8 27 64 125", "p": "4.5"},
      formula="y = yₙ + p∇yₙ + p(p+1)/2!·∇²yₙ + p(p+1)(p+2)/3!·∇³yₙ + …,  p = (x − xₙ) ÷ h")
def newton_backward(d):
    xs, ys = _xy(d)
    h, pt = _equal_spaced(xs), num(d, "p", "x")
    cols = _diff_table(ys)
    p = (pt - xs[-1]) / h
    total, term, rows = ys[-1], 1.0, [["yₙ", ys[-1]]]
    for k in range(1, len(cols)):
        term *= (p + (k - 1)) / k
        total += term * cols[k][-1]
        rows.append([f"∇{k}yₙ term", term * cols[k][-1]])
    out = Out().add("h", h).add("p", p).add("y ≈", total)
    if not (xs[0] <= pt <= xs[-1]):
        out.note("x lies outside the table, so this is extrapolation and may be inaccurate.")
    out.table("Difference table (the ∇ values read along the last entry of each column)",
              ["x", "y"] + [f"Δ{k}" for k in range(1, len(cols))],
              [[xs[i]] + [cols[k][i - k] if 0 <= i - k < len(cols[k]) else "" for k in range(len(cols))]
               for i in range(len(xs))])
    return out.table("Terms added", ["term", "value"], rows)


@tool("newton-divided-difference", "Newton's divided difference interpolation", "sem2-math", [S201 + ", Module 3"],
      "Interpolate through unequally spaced points.",
      [field("x", "x values", "vector", help="distinct, any order"), field("y", "y values", "vector"),
       field("p", "Find y at x =")],
      {"x": "0 1 2 4", "y": "1 3 7 31", "p": "3"},
      formula="y = f[x₀] + (x−x₀)f[x₀,x₁] + (x−x₀)(x−x₁)f[x₀,x₁,x₂] + …")
def newton_divided(d):
    xs, ys = _xy(d)
    if len(set(xs)) != len(xs):
        raise InputError("The x values must all be different")
    pt = num(d, "p", "x")
    n = len(xs)
    cols = [list(ys)]
    for k in range(1, n):
        prev = cols[-1]
        cols.append([(prev[i + 1] - prev[i]) / (xs[i + k] - xs[i]) for i in range(n - k)])
    total, prod = ys[0], 1.0
    for k in range(1, n):
        prod *= pt - xs[k - 1]
        total += cols[k][0] * prod
    out = Out().add("y ≈", total)
    out.table("Divided differences", ["x", "f[x]"] + [f"order {k}" for k in range(1, n)],
              [[xs[i]] + [cols[k][i] if i < len(cols[k]) else "" for k in range(n)] for i in range(n)])
    return out.note("Leading coefficients used: " + ", ".join(g(cols[k][0]) for k in range(n)) + ".")


@tool("weddle", "Weddle's rule", "sem2-math", [S201 + ", Module 5"],
      "Numerical integration with six-interval groups.",
      [field("f", "f(x)", "text"), field("a", "Lower limit"), field("b", "Upper limit"),
       field("n", "Sub-intervals (a multiple of 6)", "int", "6")],
      {"f": "1/(1+x**2)", "a": "0", "b": "1", "n": "6"},
      formula="∫f dx ≈ (3h/10)·[y₀+5y₁+y₂+6y₃+y₄+5y₅+y₆] for each group of 6, h = (b − a) ÷ n")
def weddle(d):
    f = compile_function(d["f"], ("x",))
    a, b, n = num(d, "a", "Lower limit"), num(d, "b", "Upper limit"), integer(d, "n", "Sub-intervals", 6, 6000)
    if n % 6:
        raise InputError("Weddle's rule needs the number of sub-intervals to be a multiple of 6")
    h = (b - a) / n
    ys = [f(a + i * h) for i in range(n + 1)]
    w = (1, 5, 1, 6, 1, 5, 1)
    total = sum(w[j] * ys[6 * k + j] for k in range(n // 6) for j in range(7))
    out = Out().add("h", h).add("Integral ≈", 3 * h / 10 * total)
    if n <= 24:
        out.table("Ordinates", ["i", "xᵢ", "yᵢ"], [[i, a + i * h, ys[i]] for i in range(n + 1)])
    return out


@tool("taylor-ode", "Taylor series method for y′ = f(x, y)", "sem2-math", [S201 + ", Module 5"],
      "Solve a first-order ODE with a Taylor series, using derivatives worked out symbolically.",
      [field("f", "f(x, y) in y′ = f(x, y)", "text", help="Use x and y, e.g. x + y"),
       field("x0", "x₀"), field("y0", "y₀"), field("xt", "Find y at x ="),
       field("order", "Terms up to derivative order (1 to 4)", "int", "4"),
       field("steps", "Number of steps (1 = one jump)", "int", "1")],
      {"f": "x + y", "x0": "0", "y0": "1", "xt": "0.2", "order": "4", "steps": "1"},
      formula="y(x₀+h) = y₀ + h·y′ + h²/2!·y″ + h³/3!·y‴ + …, with y″ = fₓ + f·f_y, and so on")
def taylor_ode(d):
    expr = parse_expression(d["f"], ("x", "y"))
    x0, y0, xt = num(d, "x0"), num(d, "y0"), num(d, "xt", "Target x")
    order, steps = integer(d, "order", "Order", 1, 4), integer(d, "steps", "Steps", 1, 200)
    derivs = [expr]
    for _ in range(order - 1):
        gk = derivs[-1]
        derivs.append(sympy.expand(sympy.diff(gk, X) + sympy.diff(gk, Y) * expr))
    fns = [sympy.lambdify((X, Y), e, "math") for e in derivs]
    h = (xt - x0) / steps
    x, y, rows = x0, y0, [[0, x0, y0]]
    first = []
    try:
        for s in range(1, steps + 1):
            vals = [float(fn(x, y)) for fn in fns]
            if s == 1:
                first = vals
            y = y + sum(h ** (k + 1) / math.factorial(k + 1) * vals[k] for k in range(order))
            x = x0 + s * h
            check_finite(y)
            rows.append([s, x, y])
    except (ZeroDivisionError, OverflowError, ValueError, TypeError):
        raise InputError("Could not evaluate the derivatives at these values")
    out = Out().add("h", h).add(f"y({g(xt)}) ≈", y)
    out.table("Derivatives at (x₀, y₀)", ["order", "expression", "value"],
              [[k + 1, sym(derivs[k]), first[k]] for k in range(order)])
    return out.table("Steps", ["step", "x", "y"], rows)


# ============================================================ Semester 1


def _eliminate(M, ncoef, jordan, log=None):
    """Row-reduce a Fraction matrix in place; returns the list of pivot columns."""
    rows, cols = len(M), len(M[0])
    r, pivots = 0, []

    def name(i):
        return f"R{i + 1}"

    for c in range(ncoef):
        if r >= rows:
            break
        p = next((i for i in range(r, rows) if M[i][c] != 0), None)
        if p is None:
            continue
        if p != r:
            M[r], M[p] = M[p], M[r]
            if log is not None:
                log.append(f"{name(r)} ↔ {name(p)}")
        if jordan and M[r][c] != 1:
            f = M[r][c]
            M[r] = [v / f for v in M[r]]
            if log is not None:
                log.append(f"{name(r)} → {name(r)} ÷ {g(f)}")
        for i in range(rows) if jordan else range(r + 1, rows):
            if i != r and M[i][c] != 0:
                f = M[i][c] / M[r][c]
                M[i] = [M[i][j] - f * M[r][j] for j in range(cols)]
                if log is not None:
                    log.append(f"{name(i)} → {name(i)} − ({g(f)})·{name(r)}")
        pivots.append(c)
        r += 1
    return pivots


def _show(M):
    return [[g(v) for v in row] for row in M]


@tool("rank-echelon", "Rank and echelon form", "sem1-math", [S101 + ", Module 3"],
      "Reduce a matrix to echelon form by row operations and read off its rank.",
      [field("A", "Matrix (one row per line, fractions allowed)", "matrix", rows=4)],
      {"A": "1 2 3\n2 4 6\n1 0 1"},
      formula="rank = number of non-zero rows in the echelon form")
def rank_echelon(d):
    A = matrix(d, "A", "Matrix", exact=True, max_n=8)
    M = [row[:] for row in A]
    log = []
    piv = _eliminate(M, len(M[0]), False, log)
    rank = len(piv)
    out = Out().add("Rank", str(rank)).add("Nullity (columns − rank)", str(len(M[0]) - rank))
    out.table("Echelon form", _table_cols(len(M[0]), "c"), _show(M))
    return out.table("Row operations", ["step", "operation"], [[i + 1, s] for i, s in enumerate(log)] or [["", "already in echelon form"]])


@tool("gauss-elimination", "Gauss elimination / Gauss-Jordan", "sem1-math", [S101 + ", Module 3"],
      "Solve A x = b exactly, with the row operations listed, and test consistency by rank.",
      [field("A", "Coefficient matrix A", "matrix", rows=3), field("b", "Right-hand side b", "vector"),
       field("method", "Method", "select", "gauss",
             options=[["gauss", "Gauss elimination (echelon form, back substitution)"],
                      ["jordan", "Gauss-Jordan (reduced form)"]])],
      {"A": "2 1 -1\n-3 -1 2\n-2 1 2", "b": "8 -11 -3", "method": "gauss"},
      formula="Consistent if rank A = rank [A | b]. Unique solution if that rank = number of unknowns")
def gauss_elimination(d):
    A = matrix(d, "A", "A", exact=True, max_n=8)
    m, n = len(A), len(A[0])
    b = vector(d, "b", "b", size=m, exact=True)
    aug = [A[i] + [b[i]] for i in range(m)]
    M = [r[:] for r in aug]
    log = []
    _eliminate(M, n, d["method"] == "jordan", log)
    rank_a = sum(1 for r in M if any(v != 0 for v in r[:n]))
    rank_ab = sum(1 for r in M if any(v != 0 for v in r))
    out = Out().add("rank A", str(rank_a)).add("rank [A | b]", str(rank_ab)).add("Unknowns", str(n))
    cols = _table_cols(n, "x") + ["b"]
    if rank_a < rank_ab:
        out.add("Result", "Inconsistent: no solution (a row reads 0 = non-zero)")
    else:
        R = [row[:] for row in aug]
        piv = _eliminate(R, n, True)
        free = [c for c in range(n) if c not in piv]
        if not free:
            out.add("Result", "Unique solution")
            for i, c in enumerate(piv):
                out.add(f"x{c + 1} =", g(R[i][n]))
        else:
            out.add("Result", f"Infinitely many solutions ({len(free)} free variable{'s' if len(free) > 1 else ''})")
            names = {c: f"t{k + 1}" for k, c in enumerate(free)}
            for c in free:
                out.add(f"x{c + 1} =", names[c] + " (free)")
            for i, c in enumerate(piv):
                parts = [g(R[i][n])] if R[i][n] != 0 else []
                for fc in free:
                    co = -R[i][fc]
                    if co != 0:
                        parts.append(("+ " if parts and co > 0 else "− " if co < 0 else "") +
                                     (g(abs(co)) + "·" if abs(co) != 1 else "") + names[fc])
                out.add(f"x{c + 1} =", " ".join(parts) if parts else "0")
    out.table("After elimination", cols, _show(M))
    return out.table("Row operations", ["step", "operation"], [[i + 1, s] for i, s in enumerate(log)] or [["", "none needed"]])


@tool("eigen", "Eigenvalues, eigenvectors and diagonalisation", "sem1-math", [S101 + ", Module 3"],
      "Characteristic polynomial, eigenvalues, eigenvectors, and the modal matrix P with P⁻¹AP = D.",
      [field("A", "Square matrix A (up to 6 × 6)", "matrix", rows=3)],
      {"A": "2 0 0\n0 3 4\n0 4 9"},
      formula="det(A − λI) = 0 gives the eigenvalues; (A − λI)v = 0 gives each eigenvector")
def eigen(d):
    A = np.array(matrix(d, "A", "A", square=True, max_n=6))
    n = len(A)
    coeffs = np.poly(A)
    vals, vecs = np.linalg.eig(A)
    order = np.argsort(-np.abs(vals), kind="stable")
    vals, vecs = vals[order], vecs[:, order]
    terms = []
    for i, c in enumerate(coeffs):
        c = float(c.real)
        pw = n - i
        if abs(c) < 1e-12:
            continue
        body = ("λ" if pw == 1 else f"λ^{pw}") if pw else ""
        mag = "" if (abs(abs(c) - 1) < 1e-12 and pw) else g(abs(c))
        terms.append(("−" if c < 0 else "+", mag + body))
    poly = ("−" if terms[0][0] == "−" else "") + terms[0][1] + "".join(f" {sg} {t}" for sg, t in terms[1:]) + " = 0"
    out = Out().add("Characteristic equation", poly)
    out.add("Trace (sum of eigenvalues)", g(complex(np.trace(A)))).add("Determinant (product)", g(complex(np.linalg.det(A))))
    for i, v in enumerate(vals):
        out.add(f"λ{i + 1}", g(complex(v)))
    out.table("Eigenvectors (columns, unit length)", _table_cols(n, "v"), [[g(complex(vecs[r][i])) for i in range(n)] for r in range(n)])
    if np.linalg.cond(vecs) < 1e8:
        D = np.linalg.inv(vecs) @ A @ vecs
        out.add("Diagonalisable", "Yes: P = modal matrix of the eigenvectors, D = P⁻¹AP")
        out.table("D = P⁻¹AP", _table_cols(n, "c"), [[g(complex(D[i][j])) if abs(D[i][j]) > 1e-9 else "0" for j in range(n)] for i in range(n)])
    else:
        out.add("Diagonalisable", "No: there are not enough independent eigenvectors (a repeated eigenvalue is defective)")
    return out


@tool("cayley-hamilton", "Cayley-Hamilton inverse", "sem1-math", ["1BMATM101 (Differential Calculus and Linear Algebra), Module 4–5"],
      "Characteristic polynomial, a check that A satisfies it, and A⁻¹ from it.",
      [field("A", "Square matrix A (2 × 2 to 4 × 4)", "matrix", rows=3)],
      {"A": "1 2 3\n0 1 4\n5 6 0"},
      formula="If λⁿ + c₁λⁿ⁻¹ + … + cₙ = 0, then A⁻¹ = −(Aⁿ⁻¹ + c₁Aⁿ⁻² + … + cₙ₋₁I) ÷ cₙ")
def cayley_hamilton(d):
    A = np.array(matrix(d, "A", "A", square=True, max_n=4))
    n = len(A)
    if n < 2:
        raise InputError("Use a matrix of size 2 × 2 to 4 × 4")
    c = np.poly(A)
    residual = sum(c[k] * np.linalg.matrix_power(A, n - k) for k in range(n + 1))
    out = Out().add("Characteristic polynomial coefficients [1, c₁, …, cₙ]", "[" + ", ".join(g(float(v)) for v in c) + "]")
    out.add("Largest entry of p(A)", g(float(np.max(np.abs(residual)))))
    out.note("p(A) comes out as the zero matrix (up to rounding), which is the Cayley-Hamilton theorem.")
    if abs(c[-1]) < 1e-10:
        out.add("A⁻¹", "does not exist (cₙ = det A = 0)")
        return out
    inv = -sum(c[k] * np.linalg.matrix_power(A, n - 1 - k) for k in range(n)) / c[-1]
    return out.table("A⁻¹", _table_cols(n, "c"), inv.tolist())


@tool("linear-independence", "Linear independence, basis and dimension", "sem1-math", [S101 + ", Module 4"],
      "Test whether vectors are independent, find a basis, and express the others in terms of it.",
      [field("V", "Vectors, one per line", "matrix", rows=4)],
      {"V": "1 2 3\n2 4 6\n1 0 1"},
      formula="Place the vectors as columns and row-reduce; pivot columns give a basis")
def linear_independence(d):
    V = matrix(d, "V", "Vectors", exact=True, max_n=8)
    k, dim = len(V), len(V[0])
    M = [[V[j][i] for j in range(k)] for i in range(dim)]
    piv = _eliminate(M, k, True)
    out = Out().add("Number of vectors", str(k)).add("Dimension of their span", str(len(piv)))
    out.add("Result", "Linearly independent" if len(piv) == k else "Linearly dependent")
    out.add("A basis of the span", ", ".join(f"v{c + 1}" for c in piv))
    for j in range(k):
        if j not in piv:
            terms = [f"({g(M[i][j])})·v{piv[i] + 1}" for i in range(len(piv)) if M[i][j] != 0]
            out.add(f"v{j + 1} =", " + ".join(terms) if terms else "0")
    return out


@tool("gram-schmidt", "Gram-Schmidt orthonormalisation", "sem1-math", [S101 + ", Module 4"],
      "Turn independent vectors into an orthogonal and an orthonormal set.",
      [field("V", "Vectors, one per line", "matrix", rows=3)],
      {"V": "1 1 0\n1 0 1\n0 1 1"},
      formula="uₖ = vₖ − Σⱼ<ₖ (vₖ·uⱼ ÷ uⱼ·uⱼ) uⱼ;  eₖ = uₖ ÷ ‖uₖ‖")
def gram_schmidt(d):
    V = np.array(matrix(d, "V", "Vectors", max_n=8))
    us = []
    for i, v in enumerate(V):
        u = v - sum((v @ w) / (w @ w) * w for w in us)
        if np.linalg.norm(u) < 1e-10:
            raise InputError(f"Vector {i + 1} depends on the earlier ones, so it cannot be orthogonalised")
        us.append(u)
    es = [u / np.linalg.norm(u) for u in us]
    cols = _table_cols(V.shape[1], "c")
    return (Out().table("Orthogonal vectors u", cols, [u.tolist() for u in us])
            .table("Orthonormal vectors e", cols, [e.tolist() for e in es]))


def _vars(name):
    return {"xy": (X, Y), "xyz": (X, Y, Z)}[name]


@tool("jacobian", "Jacobian determinant", "sem1-math", [S101 + ", Module 1"],
      "Partial derivatives and the Jacobian ∂(u, v, …) ÷ ∂(x, y, …).",
      [field("vars", "Variables", "select", "xy", options=[["xy", "x, y (two functions)"], ["xyz", "x, y, z (three functions)"]]),
       field("exprs", "Functions u, v (, w), one per line", "textarea", rows=3)],
      {"vars": "xy", "exprs": "x*cos(y)\nx*sin(y)"},
      formula="J = det [∂uᵢ/∂xⱼ]")
def jacobian(d):
    vs = _vars(d["vars"])
    lines = [ln for ln in d["exprs"].splitlines() if ln.strip()]
    if len(lines) != len(vs):
        raise InputError(f"Give exactly {len(vs)} functions, one per line")
    names = tuple(str(v) for v in vs)
    es = [parse_expression(ln, names) for ln in lines]
    Jm = sympy.Matrix([[sympy.diff(e, v) for v in vs] for e in es])
    det = sympy.simplify(Jm.det())
    out = Out().add("J =", sym(det))
    return out.table("Partial derivatives", ["∂/∂" + n for n in names], [[sym(sympy.simplify(c)) for c in Jm.row(i)] for i in range(Jm.rows)])


@tool("maxima-minima", "Maxima and minima of f(x, y)", "sem1-math", [S101 + ", Module 1"],
      "Stationary points of a polynomial in x and y, classified with the rt − s² test.",
      [field("f", "f(x, y) (polynomial)", "text", help="e.g. x**3 + y**3 - 3*x*y")],
      {"f": "x**3 + y**3 - 3*x*y"},
      formula="fₓ = f_y = 0.  r = fₓₓ, s = fₓ_y, t = f_yy.  rt − s² > 0: extremum (r < 0 max, r > 0 min); < 0: saddle")
def maxima_minima(d):
    f = parse_expression(d["f"], ("x", "y"))
    f = sympy.expand(sympy.nsimplify(f, rational=True))
    if not f.is_polynomial(X, Y) or sympy.Poly(f, X, Y).total_degree() > 6:
        raise InputError("Enter a polynomial in x and y of degree 6 or less (sin, exp and similar are not supported here)")
    fx, fy = sympy.diff(f, X), sympy.diff(f, Y)
    r, s, t = sympy.diff(f, X, 2), sympy.diff(f, X, Y), sympy.diff(f, Y, 2)
    out = Out().add("fₓ", sym(fx)).add("f_y", sym(fy)).add("r = fₓₓ", sym(r)).add("s = fₓ_y", sym(s)).add("t = f_yy", sym(t))
    try:
        sols = sympy.solve([fx, fy], [X, Y], dict=True)
    except Exception:
        raise InputError("Could not solve fₓ = f_y = 0 for this function")
    rows = []
    for sol in sols:
        if X not in sol or Y not in sol:
            out.note("The stationary points form a curve rather than isolated points; this tool handles isolated points only.")
            continue
        xv, yv = sympy.N(sol[X]), sympy.N(sol[Y])
        if abs(sympy.im(xv)) > 1e-9 or abs(sympy.im(yv)) > 1e-9:
            continue
        xv, yv = float(sympy.re(xv)), float(sympy.re(yv))
        rv, sv, tv = (float(e.subs({X: xv, Y: yv})) for e in (r, s, t))
        disc = rv * tv - sv * sv
        if abs(disc) < 1e-9:
            kind = "rt − s² = 0: test is inconclusive"
        elif disc < 0:
            kind = "Saddle point (neither max nor min)"
        else:
            kind = "Maximum" if rv < 0 else "Minimum" if rv > 0 else "Extremum"
        rows.append([f"({g(xv)}, {g(yv)})", g(rv), g(sv), g(tv), g(disc), g(float(f.subs({X: xv, Y: yv}))), kind])
    if not rows:
        out.note("No real stationary points found.")
        return out
    return out.table("Stationary points", ["(x, y)", "r", "s", "t", "rt − s²", "f", "Nature"], rows)


@tool("vector-calculus", "Gradient, divergence, curl, Laplacian", "sem1-math", [S101 + ", Module 2"],
      "Differential operators on scalar and vector fields, with an optional value at a point.",
      [field("op", "Operator", "select", "grad", options=[
          ["grad", "Gradient of a scalar φ"], ["div", "Divergence of F = (P, Q, R)"],
          ["curl", "Curl of F = (P, Q, R)"], ["lap", "Laplacian of a scalar φ"]]),
       field("e1", "φ, or P", "text", help="Use x, y, z"),
       field("e2", "Q (vector fields only)", "text", optional=True),
       field("e3", "R (vector fields only)", "text", optional=True),
       field("pt", "Evaluate at x, y, z (optional)", "vector", optional=True)],
      {"op": "curl", "e1": "y*z", "e2": "x*z", "e3": "x*y", "pt": "1 2 3"},
      formula="∇φ = (φₓ, φ_y, φ_z);  ∇·F = Pₓ + Q_y + R_z;  ∇×F = (R_y − Q_z, P_z − Rₓ, Qₓ − P_y)")
def vector_calculus(d):
    op = d["op"]
    vs = ("x", "y", "z")
    p1 = parse_expression(d["e1"], vs)
    if op in ("div", "curl"):
        if not d["e2"] or not d["e3"]:
            raise InputError("A vector field needs P, Q and R")
        P, Q, R = p1, parse_expression(d["e2"], vs), parse_expression(d["e3"], vs)
    pt = None
    if d["pt"]:
        pv = vector(d, "pt", "Point", size=3)
        pt = {X: pv[0], Y: pv[1], Z: pv[2]}
    if op == "grad":
        res = [sympy.diff(p1, v) for v in (X, Y, Z)]
    elif op == "div":
        res = [sympy.diff(P, X) + sympy.diff(Q, Y) + sympy.diff(R, Z)]
    elif op == "curl":
        res = [sympy.diff(R, Y) - sympy.diff(Q, Z), sympy.diff(P, Z) - sympy.diff(R, X), sympy.diff(Q, X) - sympy.diff(P, Y)]
    else:
        res = [sum(sympy.diff(p1, v, 2) for v in (X, Y, Z))]
    res = [sympy.simplify(e) for e in res]
    labels = {"grad": ["∂/∂x", "∂/∂y", "∂/∂z"], "curl": ["i component", "j component", "k component"],
              "div": ["∇·F"], "lap": ["∇²φ"]}[op]
    out = Out()
    for lab, e in zip(labels, res):
        out.add(lab, sym(e))
    if pt:
        try:
            vals = [float(e.subs(pt)) for e in res]
        except (TypeError, ValueError, ZeroDivisionError):
            raise InputError("Could not evaluate at that point")
        out.add("At the point", "(" + ", ".join(g(v) for v in vals) + ")" if len(vals) > 1 else g(vals[0]))
    if op == "curl":
        out.note("The field is irrotational (curl F = 0)." if all(e == 0 for e in res) else "The curl is non-zero, so the field is rotational.")
    if op == "div":
        out.note("The field is solenoidal (div F = 0)." if res[0] == 0 else "The divergence is non-zero, so the field is not solenoidal.")
    return out


@tool("series-expansion", "Taylor and Maclaurin series", "sem1-math", [S101 + ", Module 1"],
      "Series of f(x) about a point, up to a chosen order.",
      [field("f", "f(x)", "text", help="e.g. exp(x)*sin(x)"), field("a", "Expand about x =", "number", "0"),
       field("n", "Up to power", "int", "5")],
      {"f": "exp(x)*sin(x)", "a": "0", "n": "5"},
      formula="f(x) = f(a) + f′(a)(x−a) + f″(a)(x−a)²/2! + …  (Maclaurin when a = 0)")
def series_expansion(d):
    expr = parse_expression(d["f"], ("x",))
    a, n = num(d, "a"), integer(d, "n", "Power", 1, 10)
    try:
        s = sympy.series(expr, X, sympy.nsimplify(a), n + 1).removeO()
    except Exception:
        raise InputError("Could not expand this function about that point")
    s = sympy.expand(s) if a == 0 else s
    return (Out().add("Series", sym(s))
            .note("Terms up to (x − a)^" + str(n) + ". The expansion fails if f is not defined and smooth at the chosen point."))
