"""Registry and input helpers for the syllabus calculators (see tools_math.py, tools_physics.py).

Each calculator is a plain function that takes a dict of raw string inputs and
returns an ``Out``. The registry carries the form description, so one generic
page and one generic API route serve every calculator.
"""

import math
import re
from fractions import Fraction

from solvers import InputError, to_float, to_int

TOOLS = {}  # slug -> dict(spec + "run")


def field(name, label, kind="number", default="", help="", options=None, optional=False, rows=3):
    return {"name": name, "label": label, "kind": kind, "default": default,
            "help": help, "options": options or [], "optional": optional, "rows": rows}


def tool(slug, title, hub, syllabus, summary, fields, example, formula="", howto=""):
    """Register ``run(d) -> Out`` as a calculator.

    ``hub`` is "sem1-math", "sem2-math" or "physics". ``syllabus`` is a list of
    "COURSE, Module n" strings taken from the VTU syllabus PDFs.
    """

    def register(run):
        TOOLS[slug] = {
            "slug": slug, "title": title, "hub": hub, "syllabus": syllabus,
            "summary": summary, "fields": fields, "example": example,
            "formula": formula, "howto": howto, "run": run,
        }
        return run

    return register


def public_spec(t):
    return {k: v for k, v in t.items() if k != "run"}


def tools_for(hub):
    return [t for t in TOOLS.values() if t["hub"] == hub]


def run_tool(slug, data):
    t = TOOLS.get(slug)
    if t is None:
        raise KeyError(slug)
    clean = {}
    for f in t["fields"]:
        v = data.get(f["name"], "")
        if not isinstance(v, str):
            v = "" if v is None else str(v)
        v = v.strip()
        if len(v) > 4000:
            raise InputError(f"'{f['label']}' is too long")
        if not v and not f["optional"] and f["kind"] != "select":
            raise InputError(f"{f['label']} is required")
        if f["kind"] == "select":
            allowed = [o[0] for o in f["options"]]
            if v not in allowed:
                v = f["default"] or allowed[0]
        clean[f["name"]] = v
    return t["run"](clean).as_dict()


# ------------------------------------------------------------------ output


def g(x, digits=6):
    """Format a number compactly (6 significant figures)."""
    if isinstance(x, Fraction):
        return (str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}").replace("-", "−")
    if isinstance(x, complex):
        re_, im = x.real, x.imag
        if abs(im) < 1e-12 * max(1.0, abs(re_)):
            return g(re_, digits)
        sign = "+" if im >= 0 else "−"
        return f"{g(re_, digits)} {sign} {g(abs(im), digits)}i"
    if isinstance(x, bool) or not isinstance(x, (int, float)):
        return str(x)
    if isinstance(x, float):
        if x == 0:
            return "0"
        s = f"{x:.{digits}g}"
        return s.replace("-", "−")
    return str(x)


class Out:
    def __init__(self):
        self.summary, self.tables, self.notes = [], [], []

    def add(self, label, value):
        self.summary.append([label, value if isinstance(value, str) else g(value)])
        return self

    def table(self, title, columns, rows):
        self.tables.append({"title": title, "columns": [str(c) for c in columns],
                            "rows": [[c if isinstance(c, str) else g(c) for c in r] for r in rows]})
        return self

    def note(self, text):
        self.notes.append(text)
        return self

    def as_dict(self):
        return {"summary": self.summary, "tables": self.tables, "notes": self.notes}


# ------------------------------------------------------------------ parsing


def num(d, name, label=None, positive=False, nonneg=False):
    v = to_float(d.get(name), label or name)
    if positive and v <= 0:
        raise InputError(f"{label or name} must be greater than 0")
    if nonneg and v < 0:
        raise InputError(f"{label or name} cannot be negative")
    return v


def integer(d, name, label=None, minimum=1, maximum=100):
    return to_int(d.get(name), label or name, minimum=minimum, maximum=maximum)


def _frac(token, what):
    try:
        v = Fraction(token)
    except (ValueError, ZeroDivisionError):
        raise InputError(f"'{token}' in {what} is not a number")
    if abs(v) > 10**12:
        raise InputError(f"'{token}' in {what} is too large")
    return v


def matrix(d, name, label, square=False, max_n=8, exact=False, max_cols=None):
    """Parse a text block (one row per line) into a list of rows."""
    raw = d.get(name, "")
    rows = [[p for p in re.split(r"[,\s;]+", line.strip()) if p]
            for line in raw.splitlines() if line.strip()]
    if not rows:
        raise InputError(f"{label} is empty")
    if len(rows) > max_n or len(rows[0]) > (max_cols or max_n):
        raise InputError(f"{label} is limited to {max_n} rows and {max_cols or max_n} columns")
    if len({len(r) for r in rows}) != 1:
        raise InputError(f"Every row of {label} needs the same number of entries")
    if square and len(rows) != len(rows[0]):
        raise InputError(f"{label} must be square ({len(rows)} rows, {len(rows[0])} columns given)")
    conv = [[_frac(t, label) for t in r] for r in rows]
    return conv if exact else [[float(v) for v in r] for r in conv]


def vector(d, name, label, size=None, minimum=1, maximum=50, exact=False):
    raw = d.get(name, "")
    toks = [t for t in re.split(r"[,\s;]+", raw) if t]
    if size is not None and len(toks) != size:
        raise InputError(f"{label} needs exactly {size} values ({len(toks)} given)")
    if not (minimum <= len(toks) <= maximum):
        raise InputError(f"{label} needs between {minimum} and {maximum} values")
    vals = [_frac(t, label) for t in toks]
    return vals if exact else [float(v) for v in vals]


def check_finite(*values):
    for v in values:
        if isinstance(v, (int, float)) and not math.isfinite(v):
            raise InputError("The calculation diverged or overflowed; try different inputs")
