"""Rigorous infeasibility certificates for passive single-DOF isolation.

The point of this module
------------------------
The project's central claim is that an agent should switch design mechanism only
when it has *evidence* that the current mechanism is inadequate.  The weakest
version of that evidence is "we tried N times and failed"; the strongest is a
proof that no parameter choice within the current mechanism can ever work.

For M1 (one spring, one damper, base excitation) such a proof exists in closed
form.  Everything below is exact.

Two different peaks, and why the difference is the whole story
--------------------------------------------------------------
A passive isolator transmits ground motion through the damper as well as the
spring, so its transmissibility carries the damping term in the numerator:

    T_passive(r)^2 = (1 + (2 zeta r)^2) / ((1 - r^2)^2 + (2 zeta r)^2)        (P)

An ideal sky-hook actuator applies force without a parallel path to ground, so
its transmissibility has a constant numerator:

    T_skynook(r)^2 = 1 / ((1 - r^2)^2 + (2 zeta r)^2)                         (S)

Because of that numerator the two shapes behave qualitatively differently.

Peak of (S) (sky-hook).  Maximising 1/((1-r^2)^2 + (2 zeta r)^2) gives

    r_peak^2 = 1 - 2 zeta^2,   peak(S) = 1 / (2 zeta sqrt(1 - zeta^2))  for zeta < 1/sqrt(2),
    peak(S) = 1                                                         for zeta >= 1/sqrt(2).

So a sky-hook system can be made to never amplify: push zeta up and the peak
falls to 1.  Large damping is *good* for (S) at every frequency above resonance.

Peak of (P) (passive).  Maximising (P) gives, with D = sqrt(1 + 8 zeta^2),

    r_peak^2 = 2 / (D + 1),     peak(P) = (D + 1) / sqrt((D - 1)(D + 3)).

This is strictly decreasing in zeta but tends to 1 only as zeta -> infinity, so

    peak(P) > 1  for every finite zeta  --  a passive SDOF isolator ALWAYS
    amplifies somewhere, however heavily it is damped.

Two consequences drive the whole benchmark.  First, a task with A_max <= 1 is
unreachable by M1 outright.  Second, for any fixed peak budget the passive
mechanism needs strictly more damping than the sky-hook would, and by F3 below
more damping makes its high-frequency isolation strictly *worse*.  The passive
mechanism is therefore squeezed from both ends, and that squeeze is what the
certificate quantifies.

Derivation of the M1 certificate
--------------------------------
Write r = w / wn.  Three facts about (P), all checked numerically on a grid by
verify_monotonicity():

  F1  For zeta < 1/sqrt(2) the peak is attained at the r given above.
  F2  Beyond that r, T is strictly decreasing, with T -> 0.
  F3  For r > sqrt(2), T is strictly increasing in zeta.

Peak constraint.  T_max(zeta) decreases monotonically in zeta, so the constraint
T_max <= A_max is equivalent to zeta >= zeta_min, where zeta_min solves
T_max(zeta) = A_max.  It is found by a bracketed root find.  If A_max <= 1 no
passive SDOF can comply, since T(0) = 1 and T rises above 1 for every
zeta < 1/sqrt(2).  (Note this bites harder than the usual magnification-factor
formula 1/(2 zeta sqrt(1-zeta^2)), which is the (S) peak, not the (P) peak.)

Band constraint.  By F2 the binding frequency is the lowest one in the band, and
by F3 the most favourable admissible damping is zeta = zeta_min.  Hence the best
achievable in-band transmissibility is T(r_low; zeta_min), and requiring this not
to exceed T_iso bounds r_low from below, giving

    omega_n <= omega_low / r*(zeta_min, T_iso)

where r* solves T(r*) = T_iso.  Substituting u = r^2 into (P) gives a quadratic
with exactly one positive root whenever T_iso < 1:

    u^2 - (2 + A) u + (1 - 1/T_iso^2) = 0,   A = 4 zeta^2 (1 - T_iso^2) / T_iso^2

Sag constraint.  The support spring carries the full weight, so
delta = g / omega_n^2 <= delta_max gives

    omega_n >= omega_n_min = sqrt(g / delta_max)

Combining the last two, M1 is feasible *if and only if*

    Lambda := (omega_low / r*(zeta_min, T_iso)) / sqrt(g / delta_max)  >=  1

Lambda is a dimensionless escape-difficulty index.  Lambda < 1 certifies that the
task lies outside anything a passive SDOF isolator can ever do, and 1/Lambda is
the factor by which the two bounds are incompatible.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict

import numpy as np
from scipy.optimize import brentq

from .mechanisms import G, PassiveSDOF
from .task import IsolationTask


# --------------------------------------------------------------------------
# peak transmissibility of the two canonical second-order shapes
# --------------------------------------------------------------------------
def peak_transmissibility_sdof(zeta: float) -> float:
    """Exact peak of (P): passive SDOF, damping feedthrough included.

    Closed form  (D + 1) / sqrt((D - 1)(D + 3))  with  D = sqrt(1 + 8 zeta^2).
    Written this way it is numerically stable as zeta -> 0, where the equivalent
    expression built from r_peak^2 = (sqrt(1+8 zeta^2) - 1) / (4 zeta^2) suffers
    catastrophic cancellation.

    The peak is strictly greater than 1 for every finite zeta and tends to 1
    only as zeta -> infinity.
    """
    if zeta <= 0.0:
        return float("inf")
    D = np.sqrt(1.0 + 8.0 * zeta**2)
    den = (D - 1.0) * (D + 3.0)
    if den <= 0.0:
        # D - 1 underflows for zeta below ~1e-8; the true peak is astronomically
        # large, so report infinity rather than dividing by zero.
        return float("inf")
    return float((D + 1.0) / np.sqrt(den))


def r_peak_sdof(zeta: float) -> float:
    """Dimensionless frequency at which the passive transmissibility peaks."""
    if zeta <= 0.0:
        return 0.0
    return float(np.sqrt(2.0 / (np.sqrt(1.0 + 8.0 * zeta**2) + 1.0)))


def peak_transmissibility_skynook(zeta: float) -> float:
    """Exact peak of (S): constant numerator, i.e. no damping feedthrough."""
    if zeta <= 0.0:
        return float("inf")
    if zeta >= 1.0 / np.sqrt(2.0):
        return 1.0
    return float(1.0 / (2.0 * zeta * np.sqrt(1.0 - zeta**2)))


def zeta_min_from_peak(A_max: float, peak=peak_transmissibility_sdof) -> float:
    """Least damping ratio whose transmissibility peak stays within A_max.

    T_max is strictly decreasing in zeta on (0, 1/sqrt(2)], so the root is
    unique and a bracketed solve is exact to machine precision.
    """
    if A_max <= 1.0:
        return float("inf")
    # peak() is strictly decreasing from +inf to 1, so for A_max > 1 the root
    # exists; widen the bracket until it is straddled.
    hi = 1.0 / np.sqrt(2.0)
    while peak(hi) > A_max:
        hi *= 2.0
        if hi > 1e12:
            return float("inf")
    return float(brentq(lambda z: peak(z) - A_max, 1e-12, hi, xtol=1e-15, rtol=1e-15))


# --------------------------------------------------------------------------
# band constraint
# --------------------------------------------------------------------------
def r_star(zeta: float, T_iso: float) -> float:
    """The unique r > 1 where T(r) = T_iso, i.e. where the band constraint binds."""
    if T_iso >= 1.0:
        return 1.0
    A = 4.0 * zeta**2 * (1.0 - T_iso**2) / T_iso**2
    u = ((2.0 + A) + np.sqrt((2.0 + A) ** 2 + 4.0 * (1.0 / T_iso**2 - 1.0))) / 2.0
    return float(np.sqrt(u))


def transmissibility_sdof(r, zeta):
    """T(r) from equation (P); r is the dimensionless frequency w / wn."""
    r = np.asarray(r, dtype=float)
    return np.sqrt((1.0 + (2.0 * zeta * r) ** 2) / ((1.0 - r**2) ** 2 + (2.0 * zeta * r) ** 2))


# --------------------------------------------------------------------------
# the certificate itself
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class Certificate:
    task_name: str
    mechanism: str
    feasible: bool
    Lambda: float
    zeta_min: float
    r_star: float
    omega_n_min: float          # rad/s, lower bound imposed by static sag
    omega_n_max_allowed: float  # rad/s, upper bound imposed by the isolation band
    verdict: str

    def to_dict(self) -> dict:
        return asdict(self)

    def report(self) -> str:
        return "\n".join([
            f"[certificate] mechanism = {self.mechanism}   task = {self.task_name}",
            f"  zeta_min      = {self.zeta_min:.6f}   (least damping the peak constraint allows)",
            f"  r*            = {self.r_star:.4f}      (band constraint binds at w/wn = r*)",
            f"  omega_n >= {self.omega_n_min:.4f} rad/s   <- static sag <= delta_max        (LOWER bound)",
            f"  omega_n <= {self.omega_n_max_allowed:.4f} rad/s   <- isolation band at zeta_min   (UPPER bound)",
            f"  Lambda        = {self.Lambda:.6f}",
            f"  VERDICT: {self.verdict}",
        ])


def certify_passive_sdof(task: IsolationTask) -> Certificate:
    """Exact feasibility certificate for M1 (passive SDOF) on the given task."""
    z_min = zeta_min_from_peak(task.A_max, peak_transmissibility_sdof)
    omega_n_min = float(np.sqrt(G / task.delta_max))

    if not np.isfinite(z_min):
        return Certificate(
            task_name=task.name, mechanism=PassiveSDOF.name, feasible=False,
            Lambda=0.0, zeta_min=z_min, r_star=float("nan"),
            omega_n_min=omega_n_min, omega_n_max_allowed=float("nan"),
            verdict=("INFEASIBLE: a passive SDOF isolator has T(0) = 1 and, for every "
                     "zeta < 1/sqrt(2), a peak strictly above 1; A_max <= 1 is unreachable."),
        )

    if task.T_iso >= 1.0:
        return Certificate(
            task_name=task.name, mechanism=PassiveSDOF.name, feasible=True,
            Lambda=float("inf"), zeta_min=z_min, r_star=1.0,
            omega_n_min=omega_n_min, omega_n_max_allowed=float("inf"),
            verdict=("FEASIBLE: the band constraint is vacuous; take zeta >= zeta_min and "
                     "omega_n >= omega_n_min."),
        )

    rs = r_star(z_min, task.T_iso)
    omega_n_max = task.omega_low / rs
    lam = omega_n_max / omega_n_min
    feasible = bool(lam >= 1.0)

    if feasible:
        verdict = (
            f"FEASIBLE: sag needs omega_n >= {omega_n_min:.2f} rad/s, the band allows up to "
            f"{omega_n_max:.2f} rad/s. Witness: zeta = {z_min:.6f}, omega_n = {omega_n_max:.4f}."
        )
    else:
        verdict = (
            f"INFEASIBLE (proof): static sag requires omega_n >= {omega_n_min:.4f} rad/s, but the "
            f"isolation band at the least damping the peak constraint permits (zeta >= {z_min:.6f}) "
            f"requires omega_n <= {omega_n_max:.4f} rad/s. The two bounds are incompatible by a "
            f"factor {1 / lam:.3f}."
        )

    return Certificate(
        task_name=task.name, mechanism=PassiveSDOF.name, feasible=feasible,
        Lambda=float(lam), zeta_min=float(z_min), r_star=float(rs),
        omega_n_min=omega_n_min, omega_n_max_allowed=float(omega_n_max), verdict=verdict,
    )


# --------------------------------------------------------------------------
# independent check that the proof is not resting on a false premise
# --------------------------------------------------------------------------
def verify_monotonicity(n_zeta: int = 80, n_r: int = 5000, seed: int = 0) -> dict:
    """Numerically check assumptions F1-F3.

    Returns the worst observed violation of each property; all three must be ~0
    (or negative) for the certificate to be valid.
    """
    rng = np.random.default_rng(seed)
    r = np.logspace(-2, 2.5, n_r)
    f1 = 0.0

    for _ in range(n_zeta):
        z = float(rng.uniform(1e-3, 0.7))
        T = transmissibility_sdof(r, z)
        f1 = max(f1, float(T.max() - peak_transmissibility_sdof(z)))

    # F1b: the peak formula is also attained, not merely an upper bound
    f1b = 0.0
    for z in (0.01, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7):
        rr = np.linspace(0.5, 1.5, 400001)
        f1b = max(f1b, float(np.abs(transmissibility_sdof(rr, z).max() - peak_transmissibility_sdof(z))))

    # F2: T is non-increasing beyond its peak
    f2 = 0.0
    for _ in range(n_zeta):
        z = float(rng.uniform(1e-3, 0.7))
        T = transmissibility_sdof(r, z)
        i_pk = int(np.argmax(T))
        if i_pk + 2 < r.size:
            f2 = max(f2, float(np.diff(T[i_pk:]).max()))

    # F3: for r > sqrt(2), T increases with zeta
    f3 = 0.0
    mask = r > np.sqrt(2.0)
    for _ in range(300):
        z1 = float(rng.uniform(1e-3, 0.4))
        z2 = min(z1 + float(rng.uniform(0.01, 0.3)), 0.8)
        f3 = max(f3, float((transmissibility_sdof(r[mask], z1) - transmissibility_sdof(r[mask], z2)).max()))

    return {
        "F1_peak_is_upper_bound_max_excess": f1,
        "F1b_peak_formula_attainment_max_err": f1b,
        "F2_monotone_decrease_max_rise": f2,
        "F3_monotone_in_zeta_max_drop": f3,
    }
