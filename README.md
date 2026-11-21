# VTU Student Hub

A Student Platform for VTU Resources, Problem Solvers, CGPA & SGPA Calculators.

Designed As a side project for us to make use of the rather questionable Python Math Lab Programs, which were recently made part of the 2022 scheme of VTU.

This will also help juniors moving forward because when we were in the semester we made these calculators, we couldn't find any resources to find answers to some questions given in textbooks/classes. So, we created this website to serve as a resource for juniors to find answers quickly to verify.

For educational purposes only, we DO NOT CONDONE cheating using our website.

## Run locally

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python app.py        # http://localhost:8000
```

## Tests

```bash
pip install pytest
python -m pytest
node tests/test_grading.js   # optional: SGPA/CGPA rules, checked against VTU's printed examples
```

## Layout

- `app.py`: Flask routes and request validation
- `solvers.py`: numerical methods and the safe expression parser
- `templates/`, `static/`: pages, styles and front-end scripts
- `static/js/vtu-grading.js`: VTU grading rules (2015 to 2025 schemes), no DOM
- `tests/`: API tests and grading-rule tests

Functions are entered as expressions in `x` (and `y`), e.g. `x**2 + y`. `^` also works for powers. Supported: `sin cos tan asin acos atan sinh cosh tanh exp log ln sqrt abs`, `pi`, `e`.

Contributors: Shreyas Salankimatt, Ashray Chaitanya

Website: https://vtuhub.pythonanywhere.com/
