"""Capability profiles and the JOINT coverage structure of a requirement.

Why joint coverage
------------------
Finding 011 says a library of certificates separates log N from N only if each cuts a
constant fraction of what REMAINS.  Two certificates that rule out the same structures
compose to nothing.  So the quantity to measure is not the marginal coverage of each
constraint but the JOINT structure of the failures.

This module measures the failure structure of a requirement directly from the general
network evaluator.  It does NOT claim these evaluations are certificates - evaluating a
transfer function is exactly the expensive sampling operation a certificate is supposed
to avoid.  What it establishes is whether the CAPABILITY distribution has the
independence structure that composition needs, which is a precondition for looking for
certificates along those axes at all.
"""
from __future__ import annotations

import numpy as np

from .network import Structure


def profile(s: Structure, omega: np.ndarray, omega_low: float) -> dict:
    """Capability numbers for one structure: sag, peak, in-band attenuation."""
    T = np.abs(s.transmissibility(omega))
    band = omega >= omega_low
    return {
        "sag": s.static_deflection(),
        "peak": float(T.max()),
        "in_band": float(T[band].max()) if band.any() else float("nan"),
        "dc": float(T[0]),
    }


def requirement_check(p: dict, delta_max: float, a_max: float, t_iso: float) -> dict:
    """Which of the three sound constraints this structure violates."""
    return {
        "sag": p["sag"] > delta_max,
        "peak": p["peak"] > a_max,
        "band": p["in_band"] > t_iso,
    }


def joint_table(rows) -> dict:
    """Failure counts per constraint, and the overlap structure."""
    keys = ("sag", "peak", "band")
    n = len(rows)
    marg = {k: sum(1 for r in rows if r[k]) for k in keys}
    pair = {}
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            both = sum(1 for r in rows if r[a] and r[b])
            union = sum(1 for r in rows if r[a] or r[b])
            # conditional: given a fails, how often does b also fail?
            cond = both / marg[a] if marg[a] else 0.0
            # Jaccard overlap of the two failure sets: 1.0 means identical sets
            jac = both / union if union else 0.0
            pair[a + "|" + b] = {"both": both, "union": union,
                                 "P(b|a)": cond, "jaccard": jac}
    any_fail = sum(1 for r in rows if any(r.values()))
    all_fail = sum(1 for r in rows if all(r.values()))
    return {"n": n, "marginal": marg, "pairs": pair,
            "any": any_fail, "all": all_fail,
            "any_frac": any_fail / n if n else 0.0}
