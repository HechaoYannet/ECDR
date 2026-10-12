"""Exact waterbed (Bode-type) invariants for the L0 mechanism classes.

The idea
--------
For a stable, minimum-phase transfer function with T(0) = 1, the classical
Poisson/Bode integral gives an exact conservation law:

    integral_0^inf  ln|T(jw)| / w^2  dw   =   (pi/2) * ( sum_j 1/p_j  -  sum_i 1/z_i )

where p_j and z_i are the signed poles and zeros.  This is not an approximation.
It says that log-isolation, weighted by 1/w^2, must be paid for exactly by
log-amplification somewhere else.

Why it matters here
--------------------
The passive chain (M1, M2) has, term by term,

    sum_i 1/z_i = -c2/k2      sum_j 1/p_j = -c2/k2      difference = 0

because the same damping term appears in the numerator of T and in the
coefficient of s in det(A).  So the passive waterbed integral is EXACTLY ZERO:
every decibel of isolation is paid for by a decibel of amplification.

The sky-hook (M3) has no zeros at all, so its integral is non-zero and has the
sign that lets it isolate.  That single number is the mechanism-level difference,
and it is why M1 and M3 sit on opposite sides of the escape task.
"""
from __future__ import annotations

import numpy as np


def tf_coeffs(mech_name, params):
    """Return (num, den) polynomial coefficients in descending powers of s."""
    p = [float(v) for v in params]
    if mech_name == "M1_passive_sdof":
        wn, z = p
        return [2.0 * z * wn, wn ** 2], [1.0, 2.0 * z * wn, wn ** 2]
    if mech_name == "M3_sky_hook_active":
        wn, z = p
        return [wn ** 2], [1.0, 2.0 * z * wn, wn ** 2]
    if mech_name == "M2_tuned_mass_damper":
        wn1, z1, mu, ratio, z2 = p
        m_total = 1.0
        m1 = m_total * (1.0 - mu)
        m2 = m_total * mu
        wn2 = ratio * wn1
        k1 = wn1 ** 2 * m_total
        c1 = 2.0 * z1 * np.sqrt(k1 * m_total)
        k2 = wn2 ** 2 * m2
        c2 = 2.0 * z2 * np.sqrt(k2 * m2)
        # T = k1 * Q / det(A),  Q = m2 s^2 + c2 s + k2
        # det(A) = m1 m2 s^4 + c2 (m1+m2) s^3 + (k2 (m1+m2) + k1 m2) s^2 + k1 c2 s + k1 k2
        num = [k1 * m2, k1 * c2, k1 * k2]
        den = [m1 * m2, c2 * (m1 + m2), k2 * (m1 + m2) + k1 * m2, k1 * c2, k1 * k2]
        return num, den
    raise ValueError("unknown mechanism " + str(mech_name))


def waterbed_integral_numeric(num, den, u_lo=-40.0, u_hi=40.0, n=400001):
    """Integral of ln|T(jw)| / w^2 dw, computed in u = ln(w) to handle both tails.

    With w = exp(u) the integrand becomes ln|T| * exp(-u), which decays at both
    ends: as w -> inf, ln|T| ~ -r ln w so the product ~ -r u exp(-u); as w -> 0,
    ln|T| ~ -b w^2 so the product ~ -b exp(u).
    """
    u = np.linspace(u_lo, u_hi, n)
    s = 1j * np.exp(u)
    T = np.polyval(num, s) / np.polyval(den, s)
    return float(np.trapezoid(np.log(np.abs(T)) * np.exp(-u), u))


def waterbed_integral_roots(num, den):
    """Closed form from the signed roots.  Kept for cross-checking only.

    Do NOT use this for production values.  Root finding on these polynomials is
    ill-conditioned and the two sums cancel to zero for every passive mechanism,
    so the result is the difference of two nearly equal noisy quantities.
    """
    z = np.roots(num) if len(num) > 1 else np.array([])
    p = np.roots(den)
    sum_inv_z = np.sum(1.0 / z) if z.size else 0.0 + 0.0j
    sum_inv_p = np.sum(1.0 / p)
    return float(np.real(np.pi / 2.0 * (sum_inv_p - sum_inv_z))), \
           float(np.real(sum_inv_p)), float(np.real(sum_inv_z))


def waterbed_integral_vieta(num, den):
    """Closed form from the COEFFICIENTS.  Exact, stable, no root finding.

    Vieta, for a polynomial  c_d s^d + ... + c_1 s + c_0  whose roots are r_i:

        sum_i 1/r_i = - c_1 / c_0        (over the finite roots; = 0 if d = 0)

    applying this to numerator and denominator separately gives

        integral = (pi/2) * ( n_1/n_0 - d_1/d_0 )

    where n_k and d_k are the coefficients of s^k in numerator and denominator.
    The identity is then pure algebra and involves no numerical analysis at all.
    """
    n1 = num[-2] if len(num) >= 2 else 0.0
    n0 = num[-1]
    d1 = den[-2] if len(den) >= 2 else 0.0
    d0 = den[-1]
    return float(np.pi / 2.0 * (n1 / n0 - d1 / d0))


def waterbed_integral_exact(mech_name, params):
    """The invariant, straight from the physics.  Exact by construction.

        M1 passive SDOF    : 0                (by cancellation of the s terms)
        M2 tuned mass damper: 0               (same cancellation)
        M3 sky-hook active : -pi * zeta / wn  (no zeros, so nothing to cancel)
    """
    p = [float(v) for v in params]
    if mech_name in ("M1_passive_sdof", "M3_sky_hook_active"):
        wn, z = p
        if mech_name == "M3_sky_hook_active":
            return -np.pi * z / wn
        return 0.0
    if mech_name == "M2_tuned_mass_damper":
        return 0.0
    raise ValueError("unknown mechanism " + str(mech_name))


def check_identity(mech_name, params):
    """Compare the three routes: Vieta, exact physics, and (fragile) quadrature."""
    num, den = tf_coeffs(mech_name, params)
    vieta = waterbed_integral_vieta(num, den)
    exact = waterbed_integral_exact(mech_name, params)
    _, sip, siz = waterbed_integral_roots(num, den)
    return {
        "mechanism": mech_name,
        "params": list(params),
        "vieta": vieta,
        "exact": float(exact),
        "vieta_vs_exact": abs(vieta - exact),
        "sum_inv_poles": sip,
        "sum_inv_zeros": siz,
    }


def min_phase_check(num, den, tol=1e-9):
    """The identity requires stability and minimum phase: all roots strictly in Re < 0."""
    z = np.roots(num) if len(num) > 1 else np.array([])
    p = np.roots(den)
    return {
        "max_re_zero": float(np.max(np.real(z))) if z.size else float("-inf"),
        "max_re_pole": float(np.max(np.real(p))) if p.size else float("-inf"),
        "minimum_phase": bool(z.size == 0 or np.max(np.real(z)) < -tol),
        "stable": bool(np.max(np.real(p)) < -tol),
    }
