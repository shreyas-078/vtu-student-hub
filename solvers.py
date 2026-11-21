"""Numerical method solvers and the safe expression parser for VTU Student Hub.

Everything here is plain Python with no Flask dependency so it can be tested
directly. User-supplied expressions are never passed to ``eval`` unchecked:
they are validated against an AST whitelist first (see ``parse_expression``).
"""

import ast
import math

import sympy
from sympy import lambdify, symbols

MAX_EXPR_LENGTH = 200
MAX_STEPS = 10000


class InputError(ValueError):
    """Raised when user input is missing, malformed or unsafe."""


# Names an expression may use. Everything else is rejected.
_FUNCTIONS = {
    "sin": sympy.sin,
    "cos": sympy.cos,
    "tan": sympy.tan,
    "asin": sympy.asin,
    "acos": sympy.acos,
    "atan": sympy.atan,
    "sinh": sympy.sinh,
    "cosh": sympy.cosh,
    "tanh": sympy.tanh,
    "exp": sympy.exp,
    "log": sympy.log,
    "ln": sympy.log,
    "sqrt": sympy.sqrt,
    "abs": sympy.Abs,
}
_CONSTANTS = {"pi": sympy.pi, "e": sympy.E}

_ALLOWED_NODES = (
    ast.Expression,
    ast.BinOp,
    ast.UnaryOp,
    ast.Call,
    ast.Name,
    ast.Load,
    ast.Constant,
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.Pow,
    ast.Mod,
    ast.USub,
    ast.UAdd,
)


def parse_expression(text, variables):
    """Parse ``text`` into a sympy expression in the given variable names.

    Only numbers, the given variables, ``pi``/``e``, arithmetic operators and
    the functions in ``_FUNCTIONS`` are allowed. ``^`` is accepted as power.
    """
    if not isinstance(text, str) or not text.strip():
        raise InputError("Function is missing")
    if len(text) > MAX_EXPR_LENGTH:
        raise InputError("Function is too long")

    source = text.strip().replace("^", "**")
    try:
        tree = ast.parse(source, mode="eval")
    except SyntaxError:
        raise InputError("Function could not be understood")

    for node in ast.walk(tree):
        if not isinstance(node, _ALLOWED_NODES):
            raise InputError("Function contains unsupported syntax")
        if isinstance(node, ast.Constant) and (
            isinstance(node.value, bool) or not isinstance(node.value, (int, float))
        ):
            raise InputError("Function contains an unsupported value")
        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name) or node.func.id not in _FUNCTIONS:
                raise InputError("Unknown function in expression")
            if node.keywords:
                raise InputError("Function contains unsupported syntax")
        if isinstance(node, ast.Name) and not (
            node.id in variables or node.id in _FUNCTIONS or node.id in _CONSTANTS
        ):
            raise InputError(f"Unknown name '{node.id}' in function")

    # Use floats everywhere so huge integer powers (e.g. 9**9**9) can't hang
    # the server building exact big integers.
    class _ToFloat(ast.NodeTransformer):
        def visit_Constant(self, node):
            return ast.copy_location(ast.Constant(float(node.value)), node)

    tree = ast.fix_missing_locations(_ToFloat().visit(tree))

    namespace = {"__builtins__": {}}
    namespace.update(_FUNCTIONS)
    namespace.update(_CONSTANTS)
    namespace.update({v: symbols(v) for v in variables})
    try:
        expr = eval(compile(tree, "<expr>", "eval"), namespace)  # validated above
        return sympy.sympify(expr)
    except Exception:
        raise InputError("Function could not be evaluated")


def compile_function(text, variables):
    """Return a fast numeric callable f(*variables) for the expression."""
    expr = parse_expression(text, variables)
    syms = [symbols(v) for v in variables]
    func = lambdify(syms, expr, "math")

    def safe(*args):
        try:
            return float(func(*args))
        except (ZeroDivisionError, OverflowError, ValueError, TypeError) as exc:
            raise InputError(f"Could not evaluate function: {exc}")

    return safe


def to_float(value, name):
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise InputError(f"'{name}' must be a number")
    if not math.isfinite(number):
        raise InputError(f"'{name}' must be a finite number")
    return number


def to_int(value, name, minimum=1, maximum=MAX_STEPS):
    try:
        number = int(value)
    except (TypeError, ValueError):
        raise InputError(f"'{name}' must be a whole number")
    if number < minimum or number > maximum:
        raise InputError(f"'{name}' must be between {minimum} and {maximum}")
    return number


def number_list(values, name, count):
    if not isinstance(values, (list, tuple)) or len(values) < count:
        raise InputError(f"'{name}' needs {count} values")
    return [to_float(v, name) for v in values[:count]]


# ---------------------------------------------------------------- ODE solvers


def milne_pc(func_text, xs, ys):
    func = compile_function(func_text, ("x", "y"))
    h = xs[1] - xs[0]
    f = [func(xs[i], ys[i]) for i in range(4)]
    answer = []
    x4 = xs[3] + h
    y4p = ys[0] + (4 * h / 3) * (2 * f[1] - f[2] + 2 * f[3])
    answer.append(y4p)
    for _ in range(3):
        f4p = func(x4, y4p)
        y4c = ys[2] + (h / 3) * (f[2] + 4 * f[3] + f4p)
        y4p = y4c
        answer.append(y4c)
    return answer


def runge_kutta(func_text, x0, y0, h):
    f = compile_function(func_text, ("x", "y"))
    x1 = x0 + h
    k1 = h * f(x0, y0)
    k2 = h * f(x0 + h / 2, y0 + k1 / 2)
    k3 = h * f(x0 + h / 2, y0 + k2 / 2)
    k4 = h * f(x0 + h, y0 + k3)
    y1 = y0 + (1 / 6) * (k1 + 2 * k2 + 2 * k3 + k4)
    return [k1, k2, k3, k4, x1, y1]


def euler(func_text, x0, y0, h, n):
    f = compile_function(func_text, ("x", "y"))
    ans = []
    for _ in range(n + 1):
        y1 = y0 + h * f(x0, y0)
        x0 = x0 + h
        y0 = y1
        ans.append((round(x0, 2), round(y0, 4)))
    return ans


def mod_euler(func_text, x0, y0, h, n):
    f = compile_function(func_text, ("x", "y"))
    x1 = x0 + h
    y1e = y0 + h * f(x0, y0)
    init_guess = (x1, y1e)
    iterations = []
    y1 = y1e
    for _ in range(n):
        y1 = y0 + (h / 2) * (f(x0, y0) + f(x1, y1e))
        iterations.append(y1)
        if abs(y1 - y1e) < 0.0001:
            break
        y1e = y1
    return [init_guess, iterations, y1]


# ------------------------------------------------------------- interpolation


def interpolation(n, xs, ys, point):
    """Newton forward-difference interpolation. ``ys`` are the first column."""
    if n < 2:
        raise InputError("At least 2 data points are needed")
    y = [[0.0] * n for _ in range(n)]
    for i in range(n):
        y[i][0] = ys[i]
    for i in range(1, n):
        for j in range(n - i):
            y[j][i] = y[j + 1][i - 1] - y[j][i - 1]

    t = symbols("t")
    step = xs[1] - xs[0]
    if step == 0:
        raise InputError("x values must be distinct")
    p = (t - xs[0]) / step
    terms = [p]
    for i in range(1, n - 1):
        terms.append(terms[i - 1] * (p - i) / (i + 1))
    poly = y[0][0]
    for i in range(n - 1):
        poly = poly + y[0][i + 1] * terms[i]
    value = float(lambdify(t, sympy.simplify(poly))(point))
    return [point, value]


def lagrange(n, xs, ys, a):
    total = 0
    for i in range(n):
        u = 1
        lo = 1
        for j in range(n):
            if i != j:
                u *= a - xs[j]
                lo *= xs[i] - xs[j]
        if lo == 0:
            raise InputError("x values must be distinct")
        total += (u / lo) * ys[i]
    return [a, total]


# --------------------------------------------------------------- root finders


def newton_raphson(func_text, x0, n):
    expr = parse_expression(func_text, ("x",))
    x = symbols("x")
    f = lambdify(x, expr, "math")
    df = lambdify(x, sympy.diff(expr, x), "math")
    answer = []
    try:
        for i in range(1, n + 1):
            x1 = x0 - (f(x0) / df(x0))
            answer.append((i, float(x1), float(f(x1))))
            x0 = x1
    except (ZeroDivisionError, OverflowError, ValueError, TypeError):
        raise InputError("Method failed (zero derivative or invalid value)")
    return answer


def regula_falsi(func_text, a, b, n):
    f = compile_function(func_text, ("x",))
    answer = []
    for i in range(1, n + 1):
        denom = f(b) - f(a)
        if denom == 0:
            raise InputError("f(a) and f(b) are equal; choose a different interval")
        c = (a * f(b) - b * f(a)) / denom
        if f(a) * f(c) < 0:
            b = c
        else:
            a = c
        answer.append((i, c, f(c)))
    return answer


# ---------------------------------------------------------------- quadrature


def trapezoidal(func_text, lower, upper, n):
    f = compile_function(func_text, ("x",))
    h = (upper - lower) / n
    total = f(lower) + f(upper)
    for i in range(1, n):
        total += 2 * f(lower + i * h)
    return total * h / 2


def simpson_1_3(func_text, lower, upper, n):
    f = compile_function(func_text, ("x",))
    h = (upper - lower) / n
    total = f(lower) + f(upper)
    k = lower + h
    for i in range(1, n):
        total += (2 if i % 2 == 0 else 4) * f(k)
        k += h
    return total * h * (1 / 3)


def simpson_3_8(func_text, lower, upper, n):
    f = compile_function(func_text, ("x",))
    h = (upper - lower) / n
    total = f(lower) + f(upper)
    k = lower + h
    for i in range(1, n):
        total += (2 if i % 3 == 0 else 3) * f(k)
        k += h
    return total * 3 * h * (1 / 8)
