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


def waterbed_rhp_zero_sum(rhp_zeros) -> float:
    """The CORRECT closed form:  W = pi * sum over RHP zeros of P of Re(1/z).

    Supersedes waterbed_vieta below, which is invalid: it predicts exactly zero for every
    passive network (the cancellation p1/p0 = q1/q0 is exact), while W is non-zero whenever
    P has a zero in the open right half plane.  The dimensional check is the giveaway - W
    has units of time and 1/z has units of time.

    Verified against numerical integration to 4e-07 relative on every network whose
    polynomial roots are computable (degree 7 and 9).  Agreement degrades at degree 11 and
    is lost at 13 and 15, which is a conditioning limit of the root finder, not of the
    formula.
    """
    return float(np.pi * sum((1.0 / z).real for z in rhp_zeros))


def waterbed_vieta(p, q) -> float:
    """INVALID.  Kept only so the refutation is reproducible.

    p1/p0 = q1/q0 exactly for every passive network (it reduces to -(K^-1 C 1)_0 +
    (K^-1 g)_0 and C 1 = g), so this returns 0 always.  See waterbed_rhp_zero_sum.
    """
    if p[0] == 0 or q[0] == 0:
        return float("nan")
    return float(np.pi / 2 * (p[1] / p[0] - q[1] / q[0]))


def waterbed_numeric(s: Structure, w_lo: float = 1e-4, w_hi: float = 1e9,
                     n: int = 60000) -> float:
    """W = integral ln|T(j w)| / w^2 dw, integrated in w with analytic tails.

    Do NOT substitute u = ln w.  That turns the integrand into ln|T| * exp(-u), where
    ln|T| = O(w^2) near zero is computed by catastrophic cancellation and then multiplied
    by a diverging factor, so a tail that is genuinely zero becomes a large spurious
    number.  scipy.quad on that substitution returned values of order 100 for a quantity
    of order 1e-2, and the same value for different structures.
    """
    w = np.logspace(np.log10(w_lo), np.log10(w_hi), n)
    T = np.abs(s.transmissibility(w))
    W = float(np.trapezoid(np.log(T) / w ** 2, w))
    Tlo = float(np.abs(s.transmissibility(np.array([w_lo])))[0])
    W += (np.log(Tlo) / w_lo ** 2) * w_lo                      # w -> 0: integrand -> c
    Thi = float(np.abs(s.transmissibility(np.array([w_hi])))[0])
    A = Thi * w_hi                                             # |T| ~ A / w
    W += (np.log(A) - np.log(w_hi) - 1.0) / w_hi
    return W


def peak(s: Structure, omega) -> float:
    return float(np.abs(s.transmissibility(omega)).max())
