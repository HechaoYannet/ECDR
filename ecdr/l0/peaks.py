"""Exact peak of |T(jw)|, robust to sharp resonances.

Two numerical traps, both hit in practice
----------------------------------------
1. GRIDDING.  A light absorber with small damping, or a nearly undamped primary
   resonance, produces a peak whose width is a tiny fraction of its frequency.
   A grid steps straight over it.  Measured: a 2000-point grid under-reported a
   peak of 221745 as 1.243, a factor of 178386.

2. POLYNOMIAL EVALUATION.  The determinant expansion of the 2-DOF chain has
   coefficients spanning ~1e10 and evaluating it near a resonance cancels
   catastrophically: |D|^2 computed from the expanded polynomial came out
   NEGATIVE where the true value was tiny and positive.  The same happens one
   level down if |T|^2 is evaluated from the expanded numerator/denominator in
   x = w^2.

So the two jobs are separated.  Polynomial roots GENERATE candidate frequencies
(root finding is well conditioned here, and was verified correct).  Evaluation
uses a caller-supplied transfer function, which for the mechanisms in this
project is the 2x2 linear solve -- far better conditioned than the quartic.
"""
from __future__ import annotations

import numpy as np


def _abs_sq_poly(coeffs):
    """Coefficients of |N(jw)|^2 as a polynomial in x = w^2, ascending order."""
    c = np.asarray(coeffs, dtype=float)
    deg = c.size - 1
    re_part = np.zeros(deg + 1)
    im_part = np.zeros(deg + 1)
    for k, ck in enumerate(c):
        power = deg - k
        if power % 2 == 0:
            re_part[power] = ck * ((-1) ** (power // 2))
        else:
            im_part[power] = ck * ((-1) ** ((power - 1) // 2))
    rx = np.zeros(deg // 2 + 1)
    ix = np.zeros(deg // 2 + 1)
    for p in range(deg + 1):
        if p % 2 == 0 and re_part[p] != 0.0:
            rx[p // 2] += re_part[p]
        if p % 2 == 1 and im_part[p] != 0.0:
            ix[(p - 1) // 2] += im_part[p]
    r2 = np.convolve(rx, rx)
    i2 = np.convolve(ix, ix)
    x_i2 = np.concatenate([[0.0], i2])
    n = max(r2.size, x_i2.size)
    P = np.zeros(n)
    P[:r2.size] += r2
    P[:x_i2.size] += x_i2
    return P


def critical_omegas(num, den, tol=1e-7):
    """Positive frequencies where d/dx (|N|^2/|D|^2) = 0, x = w^2.

    Only used to GENERATE candidates; the values are evaluated elsewhere.
    """
    P = _abs_sq_poly(num)
    Q = _abs_sq_poly(den)
    dP = np.polyder(P[::-1])[::-1] if P.size > 1 else np.array([0.0])
    dQ = np.polyder(Q[::-1])[::-1] if Q.size > 1 else np.array([0.0])
    a = np.convolve(dP, Q)
    b = np.convolve(P, dQ)
    n = max(a.size, b.size)
    aa = np.zeros(n); aa[:a.size] = a
    bb = np.zeros(n); bb[:b.size] = b
    crit = aa - bb
    while crit.size > 1 and abs(crit[0]) < 1e-300:
        crit = crit[1:]
    out = []
    if crit.size > 1:
        for r in np.roots(crit[::-1]):
            if abs(r.imag) <= tol * max(1.0, abs(r.real)) and r.real > 0:
                out.append(float(np.sqrt(r.real)))
    return out


def golden_refine(tf, a, b, iters=200):
    """Maximise |tf(w)| on [a, b] by golden-section search (unimodal assumption)."""
    gr = (np.sqrt(5.0) - 1.0) / 2.0
    c = b - gr * (b - a)
    d = a + gr * (b - a)
    fc = float(np.abs(tf(np.array([c]))[0]))
    fd = float(np.abs(tf(np.array([d]))[0]))
    for _ in range(iters):
        if fc > fd:
            b, d, fd = d, c, fc
            c = b - gr * (b - a)
            fc = float(np.abs(tf(np.array([c]))[0]))
        else:
            a, c, fc = c, d, fd
            d = a + gr * (b - a)
            fd = float(np.abs(tf(np.array([d]))[0]))
    return (a + b) / 2.0


def peak_of(tf, num, den, n_grid=20000, w_lo=1e-4, w_hi=1e8, refine=True):
    """Max of |tf(w)| using polynomial roots as candidates and tf for evaluation.

    Parameters
    ----------
    tf : callable taking an array of frequencies and returning a complex array
    num, den : polynomial coefficients, used ONLY to generate candidate roots
    """
    cands = list(critical_omegas(num, den))
    w = np.logspace(np.log10(w_lo), np.log10(w_hi), n_grid)
    cands.extend(w.tolist())
    cands = np.array(sorted(c for c in cands if np.isfinite(c) and c > 0.0))

    vals = np.abs(tf(cands))
    i = int(np.argmax(vals))
    best_w = float(cands[i])
    best = float(vals[i])

    if refine:
        # refine around the best few candidates, using neighbours as brackets
        order = np.argsort(vals)[::-1][:12]
        for j in order:
            w0 = cands[j]
            lo = w0 * 0.5
            hi = w0 * 2.0
            wr = golden_refine(tf, lo, hi)
            vr = float(np.abs(tf(np.array([wr]))[0]))
            if vr > best:
                best = vr
                best_w = wr
    return best, best_w
