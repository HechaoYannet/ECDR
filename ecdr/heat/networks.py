"""Heat-exchanger NETWORKS, and the stream-specific transshipment LP that scores them.

The problem-table cascade of streams.py works on AGGREGATE heat flows: it never asks which
hot stream gives heat to which cold stream.  That is what makes it a bound over all networks
at once, and it is also why it cannot by itself demonstrate that the bound is ACHIEVABLE.

This module works at the level of a NETWORK: a set of allowed (hot, cold) matches.

WHY THERE ARE RESIDUAL VARIABLES
--------------------------------
Finding 035 recorded a model that omitted them and was 35 to 53 percent too high.  The reason
is physical.  With a minimum approach temperature, a hot stream at shifted level k can give
heat to a cold stream at level k OR ANY LOWER LEVEL - that is what it means for a hot stream
cooling from 200 to 100 to heat a cold stream from 50 to 150.  A model that forces every
interval to balance on its own forbids exactly that, and overstates the utility needed.

So heat not matched within an interval is CARRIED DOWN:

    Q_ik   hot stream i's duty in interval k
    x_ijk  heat from hot i to cold j, matched inside interval k
    RH_ik  heat from hot i in interval k carried down to k+1
    RC_jk  heat delivered to cold j in interval k from the carried pool
    qH_jk  hot utility into cold j at level k
    qC_ik  cold utility out of hot i at level k

    (hot)  sum_j x_ijk + qC_ik + RH_ik = Q_ik
    (cold) sum_i x_ijk + RC_jk + qH_jk = Q_jk
    (pool) sum_i RH_ik = sum_j RC_j,k+1        nothing carried out of the last interval
    minimise sum qH

Summing the first two over i and j and subtracting recovers the aggregate balance

    R_{k-1} + H_k + qH_k = R_k + C_k + qC_k

so with every match allowed this must reproduce the problem table, and restricting the
matches can only make it worse.  That is the property the certificate needs.
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

    allowed of None permits every compatible (hot, cold) pair, which must reproduce the
    unconstrained minimum of problem_table.
    """
    ivs = _intervals(streams, dt_min)
    K = len(ivs)
    hs = [i for i, s in enumerate(streams) if s.hot]
    cs = [j for j, s in enumerate(streams) if not s.hot]
    if allowed is None:
        allowed = set(itertools.product(hs, cs))
    pres = {k: _present(streams, dt_min, k, ivs) for k in range(K)}

    col = {}
    n = 0

    def add(key):
        nonlocal n
        col[key] = n
        n += 1

    for k in range(K):
        for (i, j) in sorted(allowed):
            if i in pres[k] and j in pres[k]:
                add(("x", i, j, k))
        for i in hs:
            if i in pres[k]:
                add(("qC", i, k))
                if k < K - 1:
                    add(("RH", i, k))
        for j in cs:
            if j in pres[k]:
                add(("qH", j, k))
                if k > 0:
                    add(("RC", j, k))

    A_eq, b_eq = [], []
    for k in range(K):
        top, bot = ivs[k]
        dt = top - bot
        for i in hs:
            if i not in pres[k]:
                continue
            row = np.zeros(n)
            for (a, b) in sorted(allowed):
                if a == i and ("x", a, b, k) in col:
                    row[col[("x", a, b, k)]] = 1.0
            row[col[("qC", i, k)]] = 1.0
            if ("RH", i, k) in col:
                row[col[("RH", i, k)]] = 1.0
            A_eq.append(row)
            b_eq.append(streams[i].cp * dt)
        for j in cs:
            if j not in pres[k]:
                continue
            row = np.zeros(n)
            for (a, b) in sorted(allowed):
                if b == j and ("x", a, b, k) in col:
                    row[col[("x", a, b, k)]] = 1.0
            row[col[("qH", j, k)]] = 1.0
            if ("RC", j, k) in col:
                row[col[("RC", j, k)]] = 1.0
            A_eq.append(row)
            b_eq.append(streams[j].cp * dt)
    # pool balance: what leaves interval k downward equals what interval k+1 receives
    for k in range(K - 1):
        row = np.zeros(n)
        any_term = False
        for i in hs:
            if ("RH", i, k) in col:
                row[col[("RH", i, k)]] += 1.0
                any_term = True
        for j in cs:
            if ("RC", j, k + 1) in col:
                row[col[("RC", j, k + 1)]] -= 1.0
                any_term = True
        if any_term:
            A_eq.append(row)
            b_eq.append(0.0)

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
