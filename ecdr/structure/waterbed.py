"""The waterbed integral for a GENERAL mechanical network.

Why this object
---------------
Finding 015 says the second certificate must live on a structural axis.  The waterbed is
the classical band-tradeoff constraint: attenuation somewhere forces amplification
elsewhere.  If it holds for an arbitrary network it is class-level by construction.

Two independent ways to get the same number, which is what makes it checkable:

  vieta     W = (pi/2) * (p1/p0 - q1/q0)   from the polynomial coefficients of P, Q
  numeric   W = integral of ln|T(j w)| / w^2  dw  over the whole axis

If the two agree, the closed form is right and the integral is well defined.  Only then
is it worth asking whether W is a structural quantity.
"""
from __future__ import annotations

import numpy as np

from .network import Structure


def polynomials(s: Structure, n_samples=None):
    """Coefficients (ascending powers) of P and Q with T = P/Q.

    Q(s) = det(M s^2 + C s + K)
    P(s) = det(A(s)) * [ A(s)^-1 (f + g s) ]_0      with A = M s^2 + C s + K

    Fit in a scaled variable t = sigma * s so the Vandermonde stays conditioned; the
    degree 2n is known, so the fit is exact up to roundoff.
    """
    M, C, K, f, g = s.matrices()
    n = s.n
    deg = 2 * n
    if n_samples is None:
        n_samples = 4 * deg + 8
    sigma = 1.0 / np.sqrt(np.max(np.abs(K)) / np.max(M))
    t = np.linspace(1.0, 6.0, n_samples)
    ss = t / sigma
    Qv = np.empty(n_samples)
    Pv = np.empty(n_samples)
    for i, si in enumerate(ss):
        A = M * si ** 2 + C * si + K
        d = np.linalg.det(A)
        Qv[i] = d
        Pv[i] = d * np.linalg.solve(A, f + g * si)[0]
    # fit in t, then convert back to s:  coefficient of s^k  =  coeff of t^k * sigma^k
    q_t = np.polynomial.polynomial.polyfit(t, Qv, deg)
    p_t = np.polynomial.polynomial.polyfit(t, Pv, deg)
    q_s = np.array([q_t[k] * sigma ** k for k in range(deg + 1)])
    p_s = np.array([p_t[k] * sigma ** k for k in range(deg + 1)])
    return p_s, q_s


def waterbed_vieta(p, q) -> float:
    """W = (pi/2) (p1/p0 - q1/q0).  Uses only the first two coefficients."""
    if p[0] == 0 or q[0] == 0:
        return float("nan")
    return float(np.pi / 2 * (p[1] / p[0] - q[1] / q[0]))


def waterbed_numeric(s: Structure, u_lo: float = -16.0, u_hi: float = 22.0,
                     n: int = 6000) -> float:
    """W = integral ln|T(j w)| / w^2 dw, evaluated in u = ln w to keep it integrable."""
    u = np.linspace(u_lo, u_hi, n)
    w = np.exp(u)
    T = np.abs(s.transmissibility(w))
    T = np.maximum(T, 1e-300)
    return float(np.trapezoid(np.log(T) * np.exp(-u), u))


def peak(s: Structure, omega) -> float:
    return float(np.abs(s.transmissibility(omega)).max())
