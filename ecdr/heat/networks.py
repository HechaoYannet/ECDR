"""Heat-exchanger NETWORKS, and the level-to-level transshipment LP that scores them.

A NETWORK here is a set of allowed (hot, cold) matches. Scoring one means asking: given only
these matches, what is the least hot utility any network can need?

WHY HEAT IS CARRIED BY MATCHED PAIRS, NOT BY A FREE POOL
-------------------------------------------------------
Finding 043 recorded a model that carried unmatched heat down through pool variables
RC[j, k] which were NOT constrained by the match set, so heat could reach a cold stream no
unit touched. An LLM agent caught it: it was offered a two-unit network as a counterexample,
pointed out that neither unit touches a particular cold stream, computed that stream's duty by
hand, and produced the correct floor where my model produced a number 7.5 kW lower.

The physics is that heat released by hot stream i at shifted level k can be absorbed by cold
stream j at shifted level k' whenever

    (i, j) is a match   and   k <= k'          (k is hotter; levels run hottest first)

because shifted temperatures already carry the half-pinch shift, so k <= k' is exactly
T_hot - T_cold >= dt_min. Transfer is therefore indexed by the PAIR of levels, not by one
level and an anonymous pool.

    QH[i,k]   hot i's duty in interval k
    QC[j,k']  cold j's need in interval k'
    x[i,j,k,k']  heat from hot i at level k to cold j at level k'
    qC[i,k]   cold utility taken from hot i at level k
    qH[j,k']  hot utility given to cold j at level k'

    (hot)  sum_{j, k' >= k} x[i,j,k,k'] + qC[i,k] = QH[i,k]
    (cold) sum_{i, k <= k'} x[i,j,k,k'] + qH[j,k'] = QC[j,k']
    minimise sum qH

With every match allowed this reduces to the transshipment relaxation and must reproduce the
problem table; restricting the matches can only raise the answer.
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
    """Least hot utility achievable using only the matches in the allowed set.

    allowed of None permits every compatible (hot, cold) pair.
    """
    ivs = _intervals(streams, dt_min)
    K = len(ivs)
    hs = [i for i, s in enumerate(streams) if s.hot]
    cs = [j for j, s in enumerate(streams) if not s.hot]
    if allowed is None:
        allowed = set(itertools.product(hs, cs))
    allowed = set(allowed)
    pres = {k: _present(streams, dt_min, k, ivs) for k in range(K)}
    dT = [ivs[k][0] - ivs[k][1] for k in range(K)]

    col, n = {}, 0

    def add(key):
        nonlocal n
        col[key] = n
        n += 1

    for (i, j) in sorted(allowed):
        for k in range(K):
            if i not in pres[k]:
                continue
            for kp in range(k, K):
                if j in pres[kp]:
                    add(("x", i, j, k, kp))
    for k in range(K):
        for i in hs:
            if i in pres[k]:
                add(("qC", i, k))
        for j in cs:
            if j in pres[k]:
                add(("qH", j, k))

    A_eq, b_eq = [], []
    for i in hs:
        for k in range(K):
            if i not in pres[k]:
                continue
            row = np.zeros(n)
            for j in cs:
                if (i, j) not in allowed:
                    continue
                for kp in range(k, K):
                    if ("x", i, j, k, kp) in col:
                        row[col[("x", i, j, k, kp)]] = 1.0
            row[col[("qC", i, k)]] = 1.0
            A_eq.append(row)
            b_eq.append(streams[i].cp * dT[k])
    for j in cs:
        for kp in range(K):
            if j not in pres[kp]:
                continue
            row = np.zeros(n)
            for i in hs:
                if (i, j) not in allowed:
                    continue
                for k in range(0, kp + 1):
                    if ("x", i, j, k, kp) in col:
                        row[col[("x", i, j, k, kp)]] = 1.0
            row[col[("qH", j, kp)]] = 1.0
            A_eq.append(row)
            b_eq.append(streams[j].cp * dT[kp])

    c = np.zeros(n)
    for key, idx in col.items():
        if key[0] == "qH":
            c[idx] = 1.0
    res = linprog(c, A_eq=np.array(A_eq), b_eq=np.array(b_eq),
                  bounds=[(0, None)] * n, method="highs")
    if not res.success:
        return {"ok": False, "message": str(res.message)}
    return {"ok": True, "Q_H": float(res.fun), "x": res.x, "col": col,
            "n_pairs": len(allowed), "n_vars": n}


def all_match_sets(streams):
    """Every subset of the compatible (hot, cold) pairs - the network space of the domain."""
    hs = [i for i, s in enumerate(streams) if s.hot]
    cs = [j for j, s in enumerate(streams) if not s.hot]
    pairs = list(itertools.product(hs, cs))
    for r in range(1, len(pairs) + 1):
        for combo in itertools.combinations(pairs, r):
            yield set(combo)
