"""Heat-exchanger NETWORKS, and the stream-specific transshipment LP that scores them.

The problem-table cascade of streams.py works on AGGREGATE heat flows: it never asks which
hot stream gives heat to which cold stream.  That is what makes it a bound over all networks
at once, and it is also why it cannot by itself demonstrate that the bound is ACHIEVABLE.

This module works at the level of a NETWORK: a set of allowed (hot, cold) matches.  Ask what
the best utility is when only those matches may exchange heat, and you have a quantity that
depends on the structure - which is what a search has to optimise, and what the certificate
has to bound.

Formulation (per shifted temperature interval k):
    hot stream i must be cooled by exactly its duty in k:
        sum_j x[i,j,k] + qC[i,k] = CP_i * dT_k
    cold stream j must be heated by exactly its duty in k:
        sum_i x[i,j,k] + qH[j,k] = CP_j * dT_k
    x[i,j,k] = 0 unless (i, j) is an allowed match
    minimise sum qH

qH is allowed at ANY level here, which is a relaxation - real utility sits at one temperature.
For the minimum-utility question that relaxation is the standard one and it is tight.
"""
from __future__ import annotations

import itertools

import numpy as np
from scipy.optimize import linprog

from .streams import _intervals


def _present(streams, dt_min, k, ivs):
    top, bot = ivs[k]
    out = []
    for idx, s in enumerate(streams):
        a, b = s.shifted(dt_min)
        lo, hi = min(a, b), max(a, b)
        if lo <= bot + 1e-12 and hi >= top - 1e-12:
            out.append(idx)
    return out


def network_lp(streams, dt_min: float, allowed=None):
    """Minimum hot utility when only the pairs in the allowed set may exchange heat.

    allowed of None means every compatible (hot, cold) pair is permitted, which reproduces
    the unconstrained minimum.  Returns the optimum and the solution.
    """
    ivs = _intervals(streams, dt_min)
    hs = [i for i, s in enumerate(streams) if s.hot]
    cs = [j for j, s in enumerate(streams) if not s.hot]
    if allowed is None:
        allowed = set(itertools.product(hs, cs))

    col = {}
    n = 0
    for k in range(len(ivs)):
        pres = _present(streams, dt_min, k, ivs)
        for (i, j) in sorted(allowed):
            if i in pres and j in pres:
                col[("x", i, j, k)] = n
                n += 1
        for j in cs:
            if j in pres:
                col[("qH", j, k)] = n
                n += 1
        for i in hs:
            if i in pres:
                col[("qC", i, k)] = n
                n += 1

    A_eq, b_eq = [], []
    for k in range(len(ivs)):
        top, bot = ivs[k]
        dt = top - bot
        pres = _present(streams, dt_min, k, ivs)
        for i in hs:
            if i not in pres:
                continue
            row = np.zeros(n)
            for (a, b) in sorted(allowed):
                if a == i and ("x", a, b, k) in col:
                    row[col[("x", a, b, k)]] = 1.0
            row[col[("qC", i, k)]] = 1.0
            A_eq.append(row)
            b_eq.append(streams[i].cp * dt)
        for j in cs:
            if j not in pres:
                continue
            row = np.zeros(n)
            for (a, b) in sorted(allowed):
                if b == j and ("x", a, b, k) in col:
                    row[col[("x", a, b, k)]] = 1.0
            row[col[("qH", j, k)]] = 1.0
            A_eq.append(row)
            b_eq.append(streams[j].cp * dt)

    c = np.zeros(n)
    for key, idx in col.items():
        if key[0] == "qH":
            c[idx] = 1.0
    res = linprog(c, A_eq=np.array(A_eq), b_eq=np.array(b_eq),
                  bounds=[(0, None)] * n, method="highs")
    if not res.success:
        return {"ok": False, "message": str(res.message)}
    return {"ok": True, "Q_H": float(res.fun), "x": res.x, "col": col,
            "n_pairs": len(allowed)}


def all_match_sets(streams):
    """Every subset of the compatible (hot, cold) pairs - the network space of the domain."""
    hs = [i for i, s in enumerate(streams) if s.hot]
    cs = [j for j, s in enumerate(streams) if not s.hot]
    pairs = list(itertools.product(hs, cs))
    for r in range(1, len(pairs) + 1):
        for combo in itertools.combinations(pairs, r):
            yield set(combo)
