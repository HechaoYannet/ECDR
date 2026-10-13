"""Step 79 - a model with UTILITIES AS NODES, and the fewest units attaining Q_H_min.

Finding 055: network_lp's "units" are process-to-process matches only. Utility heat is free - no
unit, no node. The classical U_min = N - 1 counts N as the process streams PLUS the utilities, and
a utility exchanger IS a unit. So three rounds of this thread compared quantities that count
different things.

This builds the model the classical statement is about. Nodes:

    H1, H2, C1, C2, HU (hot utility), CU (cold utility)          N = 6

Edges:
    (H_i, C_j)   a process exchanger
    (HU,  C_j)   a heater - and because HU sits above every stream, it may deliver at ANY level
    (H_i, CU)    a cooler - CU sits below every stream, so it may absorb at any level

A DESIGN is an edge set. Its unit count is the number of edges. Its hot utility is the least the LP
can achieve given which streams have utility access.

The classical claim is that a minimum-utility design exists with N - 1 = 5 units. This enumerates
every design and reports the fewest that attains Q_H_min.
"""
import _bootstrap  # noqa: F401
import itertools
import json
import pathlib

import numpy as np
from scipy.optimize import linprog

from ecdr.heat import Stream, problem_table
from ecdr.heat.networks import _present
from ecdr.heat.streams import _intervals

line = "=" * 100
STS = [Stream("H1", 150.0, 60.0, 2.0), Stream("H2", 90.0, 60.0, 8.0),
       Stream("C1", 20.0, 125.0, 2.5), Stream("C2", 100.0, 150.0, 3.0)]
DT = 10.0
PT = problem_table(STS, DT)
QH_MIN, QC_MIN = PT["Q_H_min"], PT["Q_C_min"]
NODES = ["H1", "H2", "C1", "C2", "HU", "CU"]


def design_lp(process_matches, hot_util, cold_util):
    """Least hot utility for a design: which process pairs exchange, and which streams reach a utility.

    hot_util  : set of cold-stream indices that have a heater (HU - C_j)
    cold_util : set of hot-stream indices that have a cooler (H_i - CU)
    """
    ivs = _intervals(STS, DT)
    K = len(ivs)
    hs = [i for i, s in enumerate(STS) if s.hot]
    cs = [j for j, s in enumerate(STS) if not s.hot]
    pres = {k: _present(STS, DT, k, ivs) for k in range(K)}
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
            if i in pres[k] and i in cold_util:      # only with a cooler
                add(("qC", i, k))
        for j in cs:
            if j in pres[k] and j in hot_util:       # only with a heater
                add(("qH", j, k))
    if n == 0:
        return {"ok": False}

    A_eq, b_eq = [], []
    for i in hs:
        for k in range(K):
            if i not in pres[k]:
                continue
            row = np.zeros(n)
            for (a, b) in sorted(process_matches):
                if a == i and ("x", a, b, k, k) in col:
                    pass
                if a == i:
                    for kp in range(k, K):
                        if ("x", a, b, k, kp) in col:
                            row[col[("x", a, b, k, kp)]] = 1.0
            if ("qC", i, k) in col:
                row[col[("qC", i, k)]] = 1.0
            A_eq.append(row)
            b_eq.append(STS[i].cp * dT[k])
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
            b_eq.append(STS[j].cp * dT[kp])

    c = np.zeros(n)
    for key, idx in col.items():
        if key[0] == "qH":
            c[idx] = 1.0
    res = linprog(c, A_eq=np.array(A_eq), b_eq=np.array(b_eq),
                  bounds=[(0, None)] * n, method="highs")
    if not res.success:
        return {"ok": False}
    return {"ok": True, "Q_H": float(res.fun), "x": res.x, "col": col}


PROC_PAIRS = [(0, 2), (0, 3), (1, 2), (1, 3)]
CS = [2, 3]
HS = [0, 1]

print(line)
print("THE DESIGN SPACE, with utilities as nodes")
print(line)
print("  nodes : " + ", ".join(NODES) + "     N = " + str(len(NODES))
      + "     N - 1 = " + str(len(NODES) - 1))
print("  Q_H_min = " + format(QH_MIN, ".4f") + "   Q_C_min = " + format(QC_MIN, ".4f"))

best = None
by_units = {}
total = 0
for r_pm in range(0, len(PROC_PAIRS) + 1):
    for pm in itertools.combinations(PROC_PAIRS, r_pm):
        for r_hu in range(0, len(CS) + 1):
            for hu in itertools.combinations(CS, r_hu):
                for r_cu in range(0, len(HS) + 1):
                    for cu in itertools.combinations(HS, r_cu):
                        units = len(pm) + len(hu) + len(cu)
                        if units < 3 or units > 8:
                            continue
                        total += 1
                        r = design_lp(set(pm), set(hu), set(cu))
                        if not r["ok"]:
                            continue
                        by_units.setdefault(units, []).append(r["Q_H"])
                        if r["Q_H"] <= QH_MIN + 1e-6:
                            if best is None or units < best[0]:
                                best = (units, pm, hu, cu, r["Q_H"])

print("  designs evaluated : " + str(total))
print()
print("  " + "units".rjust(6) + "designs".rjust(9) + "best Q_H".rjust(14)
      + "  attains Q_H_min".rjust(18))
for u in sorted(by_units):
    b = min(by_units[u])
    att = b <= QH_MIN + 1e-6
    print("  " + str(u).rjust(6) + str(len(by_units[u])).rjust(9) + format(b, ".6f").rjust(14)
          + ("   YES" if att else "   no").rjust(18))

print()
print(line)
print("VERDICT")
print(line)
if best:
    units, pm, hu, cu, q = best
    print("  fewest units attaining Q_H_min : " + str(units))
    print("    process exchangers : "
          + (", ".join("H" + str(i + 1) + "-C" + str(j - 1) for (i, j) in pm) or "none"))
    print("    heaters  (HU-C)    : "
          + (", ".join("C" + str(j - 1) for j in hu) or "none"))
    print("    coolers  (H-CU)    : "
          + (", ".join("H" + str(i + 1) for i in cu) or "none"))
    print()
    if units == len(NODES) - 1:
        print("  ** units = N - 1 = " + str(len(NODES) - 1) + ".  The classical bound is ATTAINED. **")
    elif units > len(NODES) - 1:
        print("  ** units = " + str(units) + " > N - 1 = " + str(len(NODES) - 1) + ". **")
        print("  The classical statement says N - 1 is ACHIEVABLE. If no design here attains")
        print("  Q_H_min with N - 1, the claim fails on this stream set - which is a real")
        print("  refutation, and the first one made against the right quantity.")
    else:
        print("  ** units = " + str(units) + " < N - 1 = " + str(len(NODES) - 1) + ". **")
        print("  Then U_min = N - 1 is refuted AS A LOWER BOUND, with utilities counted.")

out = pathlib.Path(__file__).resolve().parents[1] / "runs"
out.mkdir(exist_ok=True)
(out / "design_units.json").write_text(json.dumps({
    "Q_H_min": QH_MIN, "N": len(NODES), "designs": total,
    "by_units": {str(u): float(min(v)) for u, v in by_units.items()},
    "fewest_attaining": None if not best else {
        "units": best[0], "process": [list(m) for m in best[1]],
        "heaters": list(best[2]), "coolers": list(best[3]), "Q_H": best[4]},
}, indent=1), encoding="utf-8")
print()
print("wrote runs/design_units.json")
