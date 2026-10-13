"""Designs with the UTILITIES AS NODES, so that a utility exchanger is a unit.

Finding 055: network_lp's "units" are process-to-process matches only. Utility heat is free there.
The classical U_min = N - 1 counts the utilities in N and a utility exchanger as a unit, so three
rounds of this thread compared quantities that count different things. Finding 056 built the right
model in a script and found that the fewest units attaining Q_H_min is 5 = N - 1, with the optimal
design a spanning tree on six nodes.

This module is that model, in the library, because the orchestrator now needs it: a certificate
claiming "no design with fewer than V units attains the requirement" can be FALSIFIED by
enumeration, and the falsification result is what turns a reader that can only read into a reader
that can test.
"""
from __future__ import annotations

import itertools

import numpy as np
from scipy.optimize import linprog

from .streams import _intervals
from .networks import _present


def design_lp(streams, dt_min: float, process_matches, hot_util, cold_util):
    """Least hot utility for a design.

    process_matches : set of (hot index, cold index) that exchange heat
    hot_util        : cold indices that have a heater (HU - C_j)
    cold_util       : hot indices that have a cooler (H_i - CU)

    HU is assumed hotter than every stream and CU colder, so a heater or cooler is always
    feasible and may deliver or absorb at any level.
    """
    ivs = _intervals(streams, dt_min)
    K = len(ivs)
    hs = [i for i, s in enumerate(streams) if s.hot]
    cs = [j for j, s in enumerate(streams) if not s.hot]
    if not hot_util:
        return {"ok": False, "reason": "no heater: cold streams cannot be served"}
    pres = {k: _present(streams, dt_min, k, ivs) for k in range(K)}
    dT = [ivs[k][0] - ivs[k][1] for k in range(K)]

    col, n = {}, 0

    def add(key):
        nonlocal n
        col[key] = n
        n += 1

    for (i, j) in sorted(process_matches):
        for k in range(K):
            if i not in pres[k]:
                continue
            for kp in range(k, K):
                if j in pres[kp]:
                    add(("x", i, j, k, kp))
    for k in range(K):
        for i in hs:
            if i in pres[k] and i in cold_util:
                add(("qC", i, k))
        for j in cs:
            if j in pres[k] and j in hot_util:
                add(("qH", j, k))
    if n == 0:
        return {"ok": False, "reason": "no variables"}

    A_eq, b_eq = [], []
    for i in hs:
        for k in range(K):
            if i not in pres[k]:
                continue
            row = np.zeros(n)
            for (a, b) in sorted(process_matches):
                if a == i:
                    for kp in range(k, K):
                        if ("x", a, b, k, kp) in col:
                            row[col[("x", a, b, k, kp)]] = 1.0
            if ("qC", i, k) in col:
                row[col[("qC", i, k)]] = 1.0
            A_eq.append(row)
            b_eq.append(streams[i].cp * dT[k])
    for j in cs:
        for kp in range(K):
            if j not in pres[kp]:
                continue
            row = np.zeros(n)
            for (a, b) in sorted(process_matches):
                if b == j:
                    for k in range(0, kp + 1):
                        if ("x", a, b, k, kp) in col:
                            row[col[("x", a, b, k, kp)]] = 1.0
            if ("qH", j, kp) in col:
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
        return {"ok": False, "reason": str(res.message)}
    return {"ok": True, "Q_H": float(res.fun), "x": res.x, "col": col, "ivs": ivs}


def units_of(process_matches, hot_util, cold_util) -> int:
    return len(process_matches) + len(hot_util) + len(cold_util)


def enumerate_designs(streams, dt_min: float, max_units: int, limit: int = 6):
    """Every design with at most max_units units, scored. Returns (searched, attaining)."""
    hs = [i for i, s in enumerate(streams) if s.hot]
    cs = [j for j, s in enumerate(streams) if not s.hot]
    pairs = list(itertools.product(hs, cs))
    searched = 0
    out = []
    for r_pm in range(0, len(pairs) + 1):
        for pm in itertools.combinations(pairs, r_pm):
            for r_hu in range(0, len(cs) + 1):
                for hu in itertools.combinations(cs, r_hu):
                    for r_cu in range(0, len(hs) + 1):
                        for cu in itertools.combinations(hs, r_cu):
                            units = r_pm + r_hu + r_cu
                            if units > max_units or units == 0:
                                continue
                            if not hu:
                                continue          # without a heater no cold stream can be served
                            searched += 1
                            r = design_lp(streams, dt_min, set(pm), set(hu), set(cu))
                            if r["ok"]:
                                out.append({"units": units,
                                            "process": [list(m) for m in pm],
                                            "heaters": list(hu), "coolers": list(cu),
                                            "Q_H": r["Q_H"]})
    out.sort(key=lambda d: d["units"])
    return searched, out[:limit], out


def falsify_units(streams, dt_min: float, requirement: float, V: int):
    """Try to falsify: is there a design with FEWER than V units that attains the requirement?

    This is what a reader needs in order to TEST a unit-count certificate rather than merely read
    it. Finding 057: a reader given prose alone accepted a false certificate at confidence 0.95.
    Finding 045's reader found real defects because it had concrete cases to evaluate.
    """
    searched, sample, allf = enumerate_designs(streams, dt_min, V - 1)
    hits = [d for d in allf if d["Q_H"] <= requirement + 1e-6]
    hits.sort(key=lambda d: d["units"])
    return {"searched": searched, "counterexamples": hits[:4], "n_hits": len(hits),
            "max_units_searched": V - 1}
