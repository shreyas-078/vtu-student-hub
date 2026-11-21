"""Physics calculators for the VTU first-year syllabus.

Course codes and topics come from the VTU 2025 scheme syllabus PDFs
(https://vtu.ac.in/en/b-e-scheme-syllabus/). Constants are the exact SI
(2019) values or CODATA 2018 values.
"""

import cmath
import math
import re

import numpy as np

from solvers import InputError
from toolkit import Out, field, g, integer, matrix, num, tool, vector

H = 6.62607015e-34       # Planck constant, J s
HBAR = H / (2 * math.pi)
E = 1.602176634e-19      # elementary charge, C
KB = 1.380649e-23        # Boltzmann constant, J/K
C = 299792458.0          # speed of light, m/s
MU0 = 1.25663706212e-6   # vacuum permeability, N/A^2
PARTICLES = {            # name: (mass kg, charge in units of e)
    "electron": (9.1093837015e-31, 1),
    "proton": (1.67262192369e-27, 1),
    "neutron": (1.67492749804e-27, 0),
    "alpha": (6.6446573357e-27, 2),
}
PARTICLE_OPTIONS = [["electron", "Electron"], ["proton", "Proton"], ["neutron", "Neutron"], ["alpha", "Alpha particle"]]
Q = "1BPHYS102 (Quantum Physics and Applications)"
QEC = "1BPHEC102 (Quantum Physics and Electronic Sensors)"
QEE = "1BPHEE102 (Engineering Materials)"


def particle(d, name="particle"):
    return PARTICLES[d[name]]


def ev(joule):
    return joule / E


# ------------------------------------------------------------------ Module 1


@tool("de-broglie", "de Broglie wavelength", "physics", [Q + ", Module 1", QEC + ", Module 1"],
      "Wavelength of a particle from its accelerating voltage, kinetic energy or speed.",
      [field("particle", "Particle", "select", "electron", options=PARTICLE_OPTIONS),
       field("mode", "Known quantity", "select", "voltage", options=[
           ["voltage", "Accelerating voltage (V)"], ["energy", "Kinetic energy (eV)"], ["speed", "Speed (m/s)"]]),
       field("value", "Value")],
      {"particle": "electron", "mode": "voltage", "value": "100"},
      formula="λ = h ÷ p,  p = √(2mK) = √(2mqV) = mv   (non-relativistic)")
def de_broglie(d):
    m, charge = particle(d)
    v = num(d, "value", "Value", positive=True)
    if d["mode"] == "voltage":
        if charge == 0:
            raise InputError("A neutron has no charge, so a voltage cannot accelerate it; use kinetic energy or speed")
        ke = charge * E * v
    elif d["mode"] == "energy":
        ke = v * E
    else:
        if v >= C:
            raise InputError("Speed must be below the speed of light")
        ke = 0.5 * m * v * v
    p = math.sqrt(2 * m * ke) if d["mode"] != "speed" else m * v
    lam = H / p
    speed = p / m
    out = (Out().add("Wavelength λ (m)", lam).add("λ (nm)", lam * 1e9).add("λ (Å)", lam * 1e10)
           .add("Momentum p (kg m/s)", p).add("Speed v (m/s)", speed).add("Kinetic energy (eV)", ev(ke)))
    if speed > 0.1 * C:
        out.note("The speed is above 10% of c, so the non-relativistic formula loses accuracy.")
    return out


@tool("uncertainty", "Heisenberg uncertainty", "physics", [Q + ", Module 1", QEC + ", Module 1", QEE + ", Module 1"],
      "Minimum momentum or energy spread from the uncertainty principle (including spectral-line broadening).",
      [field("mode", "Known quantity", "select", "x", options=[["x", "Position spread Δx"], ["t", "Lifetime Δt (line width)"]]),
       field("particle", "Particle (for Δx)", "select", "electron", options=PARTICLE_OPTIONS),
       field("value", "Δx in nm, or Δt in seconds")],
      {"mode": "x", "particle": "electron", "value": "0.1"},
      formula="Δx·Δp ≥ ħ ÷ 2,   ΔE·Δt ≥ ħ ÷ 2")
def uncertainty(d):
    v = num(d, "value", "Value", positive=True)
    if d["mode"] == "x":
        m, _ = particle(d)
        dp = HBAR / (2 * v * 1e-9)
        return (Out().add("Minimum Δp (kg m/s)", dp).add("Minimum Δv (m/s)", dp / m)
                .note("Taking the minimum-uncertainty case (equality)."))
    de = HBAR / (2 * v)
    return (Out().add("Minimum ΔE (J)", de).add("Minimum ΔE (eV)", ev(de)).add("Line width Δν = ΔE ÷ h (Hz)", de / H)
            .note("A short-lived excited state gives a broad spectral line."))


@tool("particle-in-box", "Particle in a 1-D infinite well", "physics", [Q + ", Module 1", QEC + ", Module 1"],
      "Energy levels of a particle in a box, and the probability of finding it in a region.",
      [field("particle", "Particle", "select", "electron", options=PARTICLE_OPTIONS),
       field("L", "Width of the well L (nm)"), field("n", "Show levels up to n", "int", "5"),
       field("state", "State n for the probability (optional)", "int", "1", optional=True),
       field("x1", "From x₁ (nm, optional)", optional=True), field("x2", "To x₂ (nm, optional)", optional=True)],
      {"particle": "electron", "L": "1", "n": "5", "state": "1", "x1": "0.25", "x2": "0.75"},
      formula="Eₙ = n²h² ÷ (8mL²);  ψₙ = √(2/L)·sin(nπx/L);  P = ∫ψ² dx from x₁ to x₂")
def particle_in_box(d):
    m, _ = particle(d)
    L = num(d, "L", "L", positive=True) * 1e-9
    n = integer(d, "n", "n", 1, 50)
    rows = [[k, k * k * H * H / (8 * m * L * L), ev(k * k * H * H / (8 * m * L * L)), k - 1] for k in range(1, n + 1)]
    out = Out().table("Energy levels", ["n", "Eₙ (J)", "Eₙ (eV)", "nodes inside the well"], rows)
    if d["x1"] and d["x2"]:
        k = integer(d, "state", "State n", 1, 50)
        x1, x2 = num(d, "x1") * 1e-9, num(d, "x2") * 1e-9
        if not (0 <= x1 < x2 <= L):
            raise InputError("Need 0 ≤ x₁ < x₂ ≤ L")
        a = k * math.pi / L
        p = (x2 - x1) / L - (math.sin(2 * a * x2) - math.sin(2 * a * x1)) / (2 * k * math.pi)
        out.summary.insert(0, [f"Probability in [{g(x1 * 1e9)}, {g(x2 * 1e9)}] nm for n = {k}", g(p)])
    if n >= 2:
        out.note(f"Photon emitted in the {n} → {n - 1} transition: {g(H * C / (rows[-1][1] - rows[-2][1]) * 1e9)} nm.")
    return out


# ------------------------------------------------------------------ Module 2


@tool("fermi-energy", "Fermi energy of a metal", "physics", [Q + ", Module 2", QEC + ", Module 2", QEE + ", Module 2"],
      "Fermi energy at 0 K from the free-electron concentration.",
      [field("n", "Electron concentration n (m⁻³)", help="e.g. 8.5e28 for copper")],
      {"n": "8.49e28"},
      formula="E_F = (h² ÷ 8m)·(3n ÷ π)^(2/3)")
def fermi_energy(d):
    n = num(d, "n", "n", positive=True)
    m = PARTICLES["electron"][0]
    ef = H * H / (8 * m) * (3 * n / math.pi) ** (2 / 3)
    vf = math.sqrt(2 * ef / m)
    return (Out().add("E_F (J)", ef).add("E_F (eV)", ev(ef)).add("Fermi speed (m/s)", vf)
            .add("Fermi temperature (K)", ef / KB))


@tool("fermi-factor", "Fermi-Dirac factor", "physics", [Q + ", Module 2", QEC + ", Module 2", QEE + ", Module 2"],
      "Probability that a state at energy E is occupied at temperature T.",
      [field("E", "Energy E (eV)"), field("EF", "Fermi energy E_F (eV)"), field("T", "Temperature T (K)")],
      {"E": "7.1", "EF": "7.0", "T": "300"},
      formula="f(E) = 1 ÷ (1 + e^((E − E_F) ÷ kT))")
def fermi_factor(d):
    e_, ef, t = num(d, "E"), num(d, "EF"), num(d, "T", "T", positive=True)
    x = (e_ - ef) * E / (KB * t)
    f = 0.0 if x > 700 else 1.0 if x < -700 else 1 / (1 + math.exp(x))
    out = Out().add("f(E)", f).add("kT (eV)", KB * t / E)
    if e_ == ef:
        out.note("At E = E_F the factor is exactly ½ at any temperature above 0 K.")
    return out


@tool("hall-effect", "Hall effect", "physics", [Q + ", Module 2", QEE + ", Module 2"],
      "Hall coefficient, carrier concentration and type from a Hall measurement.",
      [field("I", "Current I (mA)"), field("B", "Magnetic field B (T)"), field("t", "Sample thickness t (mm)"),
       field("VH", "Hall voltage V_H (mV, negative if measured so)"),
       field("sigma", "Conductivity σ (S/m, optional, gives mobility)", optional=True)],
      {"I": "10", "B": "0.5", "t": "0.5", "VH": "2", "sigma": "100"},
      formula="R_H = V_H·t ÷ (I·B),  n = 1 ÷ (|R_H|·e),  μ = |R_H|·σ")
def hall_effect(d):
    i, b, t, vh = num(d, "I") * 1e-3, num(d, "B", "B", positive=True), num(d, "t", "t", positive=True) * 1e-3, num(d, "VH") * 1e-3
    if i == 0 or vh == 0:
        raise InputError("I and V_H must be non-zero")
    rh = vh * t / (i * b)
    out = (Out().add("R_H (m³/C)", rh).add("Carrier concentration n (m⁻³)", 1 / (abs(rh) * E))
           .add("Carriers", "electrons (n-type)" if rh < 0 else "holes (p-type)"))
    if d["sigma"]:
        out.add("Mobility μ (m²/V s)", abs(rh) * num(d, "sigma", "σ", positive=True))
    return out


# ------------------------------------------------------------------ Module 3


@tool("superconductor", "Critical field and critical current", "physics", [Q + ", Module 3", QEC + ", Module 3", QEE + ", Module 3"],
      "H_c(T) and the Silsbee critical current of a superconducting wire.",
      [field("Hc0", "H_c(0) (A/m)", help="e.g. 6.5e4 for lead"), field("Tc", "Critical temperature T_c (K)"),
       field("T", "Temperature T (K)"), field("r", "Wire radius r (mm)")],
      {"Hc0": "6.5e4", "Tc": "7.2", "T": "5", "r": "1"},
      formula="H_c(T) = H_c(0)·[1 − (T/T_c)²];  I_c = 2πr·H_c  (Silsbee);  Φ₀ = h ÷ 2e")
def superconductor(d):
    hc0, tc, t, r = num(d, "Hc0", "H_c(0)", positive=True), num(d, "Tc", "T_c", positive=True), num(d, "T", "T", nonneg=True), num(d, "r", "r", positive=True) * 1e-3
    if t >= tc:
        raise InputError("At or above T_c the material is not superconducting, so there is no critical field")
    hc = hc0 * (1 - (t / tc) ** 2)
    return (Out().add("H_c(T) (A/m)", hc).add("B_c = μ₀H_c (T)", MU0 * hc).add("Critical current I_c (A)", 2 * math.pi * r * hc)
            .add("Flux quantum Φ₀ (Wb)", H / (2 * E)))


# ------------------------------------------------------------------ Module 4


@tool("einstein-coefficients", "Einstein A and B coefficients", "physics", [Q + ", Module 4", QEC + ", Module 4"],
      "Spontaneous-to-stimulated emission ratio and level populations for a transition.",
      [field("lam", "Wavelength λ (nm)"), field("T", "Temperature T (K, optional)", optional=True)],
      {"lam": "632.8", "T": "300"},
      formula="A₂₁ ÷ B₂₁ = 8πhν³ ÷ c³;  N₂ ÷ N₁ = e^(−hν/kT);  (spontaneous ÷ stimulated rate) = e^(hν/kT) − 1")
def einstein(d):
    lam = num(d, "lam", "λ", positive=True) * 1e-9
    nu = C / lam
    out = Out().add("Frequency ν (Hz)", nu).add("Photon energy hν (eV)", ev(H * nu)).add("A₂₁ ÷ B₂₁ (J s/m³)", 8 * math.pi * H * nu ** 3 / C ** 3)
    if d["T"]:
        t = num(d, "T", "T", positive=True)
        x = H * nu / (KB * t)
        if x > 700:
            out.add("N₂ ÷ N₁ at T", "≈ 0 (below 1e-300)")
        else:
            out.add("N₂ ÷ N₁ at T", math.exp(-x)).add("Spontaneous ÷ stimulated rate at T", math.expm1(x))
            out.note("At thermal equilibrium N₂ < N₁, so absorption beats stimulated emission. Lasing needs population inversion.")
    return out


@tool("optical-fibre", "Optical fibre: NA, V-number, modes", "physics", [Q + ", Module 4", QEC + ", Module 4"],
      "Numerical aperture, acceptance angle, V-number and number of modes of a step-index fibre.",
      [field("n1", "Core index n₁"), field("n2", "Cladding index n₂"), field("n0", "Outside medium index n₀", "number", "1"),
       field("a", "Core radius a (µm)"), field("lam", "Wavelength λ (nm)")],
      {"n1": "1.48", "n2": "1.46", "n0": "1", "a": "25", "lam": "850"},
      formula="NA = √(n₁² − n₂²);  θ₀ = sin⁻¹(NA ÷ n₀);  V = 2πa·NA ÷ λ;  modes ≈ V² ÷ 2")
def optical_fibre(d):
    n1, n2, n0 = num(d, "n1", "n₁", positive=True), num(d, "n2", "n₂", positive=True), num(d, "n0", "n₀", positive=True)
    if n1 <= n2:
        raise InputError("The core index n₁ must be larger than the cladding index n₂")
    a, lam = num(d, "a", "a", positive=True) * 1e-6, num(d, "lam", "λ", positive=True) * 1e-9
    na = math.sqrt(n1 * n1 - n2 * n2)
    out = Out().add("Numerical aperture NA", na).add("Fractional index change Δ = (n₁−n₂)/n₁", (n1 - n2) / n1)
    if na / n0 > 1:
        out.add("Acceptance angle θ₀", "90° (NA ÷ n₀ ≥ 1, so every ray is accepted)")
    else:
        out.add("Acceptance angle θ₀ (degrees)", math.degrees(math.asin(na / n0)))
    v = 2 * math.pi * a * na / lam
    out.add("V-number", v).add("Approximate number of modes V²/2", v * v / 2)
    out.add("Operation", "Single-mode (V < 2.405)" if v < 2.405 else "Multimode")
    return out


# ------------------------------------------------------------------ Module 5

_S2 = 1 / math.sqrt(2)
GATES1 = {
    "X": np.array([[0, 1], [1, 0]], complex),
    "Y": np.array([[0, -1j], [1j, 0]], complex),
    "Z": np.array([[1, 0], [0, -1]], complex),
    "H": np.array([[_S2, _S2], [_S2, -_S2]], complex),
    "S": np.array([[1, 0], [0, 1j]], complex),
    "T": np.array([[1, 0], [0, cmath.exp(1j * math.pi / 4)]], complex),
}


def _amp(z):
    return g(complex(z), 4)


def _ket(vec, n):
    return " + ".join(f"({_amp(v)})|{format(i, f'0{n}b')}⟩" for i, v in enumerate(vec) if abs(v) > 1e-12) or "0"


@tool("qubit-gates", "Single-qubit state and gates", "physics", [Q + ", Module 5", QEC + ", Module 5"],
      "Apply X, Y, Z, H, S, T gates in order to a qubit and read probabilities and the Bloch sphere position.",
      [field("a", "Amplitude α of |0⟩", "text", "1", help="real or complex, e.g. 0.6 or 0.5+0.5j"),
       field("b", "Amplitude β of |1⟩", "text", "0"),
       field("gates", "Gates in order", "text", "H T H", optional=True, help="letters X Y Z H S T separated by spaces; first gate is applied first")],
      {"a": "1", "b": "0", "gates": "H T H"},
      formula="|ψ⟩ = α|0⟩ + β|1⟩;  P(0) = |α|², P(1) = |β|²;  Bloch: θ = 2cos⁻¹|α|,  φ = arg β − arg α")
def qubit_gates(d):
    try:
        a, b = complex(d["a"].replace(" ", "").replace("i", "j")), complex(d["b"].replace(" ", "").replace("i", "j"))
    except ValueError:
        raise InputError("α and β must be numbers, like 0.6 or 0.5+0.5j")
    nrm = math.sqrt(abs(a) ** 2 + abs(b) ** 2)
    if nrm == 0 or not math.isfinite(nrm):
        raise InputError("α and β cannot both be zero")
    v = np.array([a, b]) / nrm
    out = Out()
    if abs(nrm - 1) > 1e-6:
        out.note(f"The amplitudes were scaled by 1/{g(nrm)} so that |α|² + |β|² = 1.")
    rows = [["start", _ket(v, 1), g(abs(v[0]) ** 2), g(abs(v[1]) ** 2)]]
    seq = d["gates"].replace(",", " ").upper().split()
    if len(seq) > 20:
        raise InputError("Use at most 20 gates")
    for s in seq:
        if s not in GATES1:
            raise InputError(f"Unknown gate '{s}'. Use X, Y, Z, H, S or T")
        v = GATES1[s] @ v
        rows.append([s, _ket(v, 1), g(abs(v[0]) ** 2), g(abs(v[1]) ** 2)])
    theta = 2 * math.acos(min(1.0, abs(v[0])))
    phi = (cmath.phase(v[1]) - cmath.phase(v[0])) % (2 * math.pi) if abs(v[0]) > 1e-9 and abs(v[1]) > 1e-9 else 0.0
    out.add("Final state", _ket(v, 1)).add("P(measure 0)", abs(v[0]) ** 2).add("P(measure 1)", abs(v[1]) ** 2)
    out.add("Bloch angle θ (degrees)", math.degrees(theta)).add("Bloch angle φ (degrees)", math.degrees(phi))
    out.add("Bloch vector (x, y, z)", f"({g(math.sin(theta) * math.cos(phi), 4)}, {g(math.sin(theta) * math.sin(phi), 4)}, {g(math.cos(theta), 4)})")
    return out.table("After each gate", ["gate", "state", "P(0)", "P(1)"], rows)


@tool("two-qubit-gates", "Two-qubit circuits (CNOT, Bell states)", "physics", [Q + ", Module 5"],
      "Run a short circuit of single-qubit gates and CNOT on two qubits.",
      [field("start", "Starting state", "select", "00", options=[["00", "|00⟩"], ["01", "|01⟩"], ["10", "|10⟩"], ["11", "|11⟩"]]),
       field("circuit", "Circuit", "text", "H0 CNOT01", help="Gate then qubit number: H0, X1, Z0, S1, T0. CNOT01 = control qubit 0, target qubit 1; CNOT10 the reverse. Left to right.")],
      {"start": "00", "circuit": "H0 CNOT01"},
      formula="Qubit 0 is the left bit. H0 on |00⟩ gives (|00⟩+|10⟩)/√2, then CNOT01 gives the Bell state (|00⟩+|11⟩)/√2")
def two_qubit(d):
    v = np.zeros(4, complex)
    v[int(d["start"], 2)] = 1
    I2 = np.eye(2, dtype=complex)
    cnot01 = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]], complex)
    cnot10 = np.array([[1, 0, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0], [0, 1, 0, 0]], complex)
    toks = d["circuit"].replace(",", " ").upper().split()
    if len(toks) > 20:
        raise InputError("Use at most 20 gates")
    rows = [["start", _ket(v, 2)]]
    for t in toks:
        if t in ("CNOT01", "CNOT10"):
            U = cnot01 if t == "CNOT01" else cnot10
        else:
            m = re.fullmatch(r"([XYZHST])([01])", t)
            if not m:
                raise InputError(f"Could not read '{t}'. Use e.g. H0, X1, CNOT01")
            U = np.kron(GATES1[m.group(1)], I2) if m.group(2) == "0" else np.kron(I2, GATES1[m.group(1)])
        v = U @ v
        rows.append([t, _ket(v, 2)])
    out = Out().add("Final state", _ket(v, 2))
    for i in range(4):
        out.add(f"P(|{i:02b}⟩)", abs(v[i]) ** 2)
    # entangled if the 2x2 amplitude matrix has rank 2
    sv = np.linalg.svd(v.reshape(2, 2), compute_uv=False)
    out.add("Entangled", "Yes (cannot be written as a product of two single-qubit states)" if sv[1] > 1e-9 else "No (a product state)")
    return out.table("After each gate", ["gate", "state"], rows)


# ------------------------------------------------------ Civil / materials streams


@tool("sabine-reverberation", "Sabine reverberation time", "physics", ["1BPHYC102 (Physics for Sustainable Structural Systems), Module 3"],
      "Reverberation time of a hall from its volume and surface absorption.",
      [field("V", "Volume V (m³)"), field("S", "Surfaces: area (m²) and absorption coefficient, one pair per line", "matrix", rows=4,
                                            help="e.g. 200 0.03 for 200 m² of plaster")],
      {"V": "2000", "S": "200 0.03\n150 0.60\n300 0.15"},
      formula="T = 0.161·V ÷ Σ(aᵢSᵢ)  (seconds, V in m³, S in m²)")
def sabine(d):
    V = num(d, "V", "V", positive=True)
    rows = matrix(d, "S", "Surfaces", max_n=20, max_cols=2)
    if len(rows[0]) != 2:
        raise InputError("Each line needs an area and an absorption coefficient")
    if any(s <= 0 or not (0 <= a <= 1) for s, a in rows):
        raise InputError("Areas must be positive and absorption coefficients between 0 and 1")
    total = sum(s * a for s, a in rows)
    if total == 0:
        raise InputError("Total absorption is zero")
    area = sum(s for s, _ in rows)
    return (Out().add("Total absorption (sabins, m²)", total).add("Mean absorption coefficient", total / area)
            .add("Reverberation time T (s)", 0.161 * V / total))


@tool("springs", "Springs in series and parallel", "physics", ["1BPHYC102 (Physics for Sustainable Structural Systems), Module 1", "1BPHYM102 (Physics of Materials), Module 1"],
      "Equivalent stiffness and the period of a mass on the combination.",
      [field("k", "Spring constants (N/m)", "vector", help="two or more values"),
       field("how", "Combination", "select", "series", options=[["series", "Series"], ["parallel", "Parallel"]]),
       field("m", "Mass m (kg)")],
      {"k": "200 300", "how": "series", "m": "0.5"},
      formula="Series: 1/k = Σ1/kᵢ.  Parallel: k = Σkᵢ.  T = 2π√(m ÷ k)")
def springs(d):
    ks = vector(d, "k", "Spring constants", minimum=2, maximum=20)
    if any(k <= 0 for k in ks):
        raise InputError("Spring constants must be positive")
    m = num(d, "m", "m", positive=True)
    keq = 1 / sum(1 / k for k in ks) if d["how"] == "series" else sum(ks)
    t = 2 * math.pi * math.sqrt(m / keq)
    return Out().add("Equivalent k (N/m)", keq).add("Period T (s)", t).add("Frequency f (Hz)", 1 / t)
