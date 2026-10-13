"""Step 69 - the model's objection to my counterexample, tested.

The derive loop offered this as a refutation of V = 3:

    units = 2,  Q_H = 142.500 kW,  matches = [[0, 2], [1, 2]]
    with 0=H1, 1=H2, 2=C1, 3=C2

so the two units are H1-C1 and H2-C1. **Neither unit touches C2.** The model refused to accept
it and said: "the claimed 2-unit network leaves C2 unheated, so hot utility >= 150 kW."

C2 is 100 -> 150 C at cp 3.0, a duty of 150.0 kW. If no exchanger touches C2, every one of
those 150 kW must come from hot utility, so ANY network with these two matches needs at least
150 kW - more than the 142.5 the LP reported.

The model is right, and the cause is in my own model. network_lp carries heat down through the
pool variables RC[j,k] and lets them deliver to ANY cold stream, whether or not that stream has
a match. So restricting the matches does not restrict the heat that can reach a stream, and the
model reports a utility a non-existent network would need.
"""
import _bootstrap  # noqa: F401
import numpy as np
from scipy.optimize import linprog

from ecdr.heat import Stream, network_lp, problem_table
from ecdr.heat.networks import _present
from ecdr.heat.streams import _intervals

line = "=" * 92
STS = [Stream("H1", 150.0, 60.0, 2.0), Stream("H2", 90.0, 60.0, 8.0),
       Stream("C1", 20.0, 125.0, 2.5), Stream("C2", 100.0, 150.0, 3.0)]
DT = 10.0
MATCHES = {(0, 2), (1, 2)}

print(line)
print("the counterexample network: matches H1-C1 and H2-C1, C2 untouched")
print(line)
print("  C2 duty = 3.0 * (150 - 100) = 150.000 kW, all of it from hot utility")
print("  so ANY network with only these matches needs Q_H >= 150.000")
print()

r = network_lp(STS, DT, allowed=MATCHES)
print("  network_lp with these matches          : Q_H = " + format(r["Q_H"], ".6f"))
print("  the model's figure                     : Q_H >= 150.000")
print("  the LP is below the model's floor by   : " + format(150.0 - r["Q_H"], ".6f"))
print()

# Direct test: rebuild the same LP but forbid pool heat reaching an UNMATCHED cold stream.
def lp_unmatched_pool_forbidden(streams, dt_min, allowed):
    ivs = _intervals(streams, dt_min)
    K = len(ivs)
    hs = [i for i, s in enumerate(streams) if s.hot]
    cs = [j for j, s in enumerate(streams) if not s.hot]
    touched = {j for (_, j) in allowed}
    pres = {k: _present(streams, dt_min, k, ivs) for k in range(K)}
    col, n = {}, 0
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
                if k > 0 and j in touched:      # <-- only matched colds get pool heat
                    add(("RC", j, k))
    A, b = [], []
    for k in range(K):
        dt = ivs[k][0] - ivs[k][1]
        for i in hs:
            if i not in pres[k]:
                continue
            row = np.zeros(n)
            for (a, c) in sorted(allowed):
                if a == i and ("x", a, c, k) in col:
                    row[col[("x", a, c, k)]] = 1.0
            row[col[("qC", i, k)]] = 1.0
            if ("RH", i, k) in col:
                row[col[("RH", i, k)]] = 1.0
            A.append(row); b.append(streams[i].cp * dt)
        for j in cs:
            if j not in pres[k]:
                continue
            row = np.zeros(n)
            for (a, c) in sorted(allowed):
                if c == j and ("x", a, c, k) in col:
                    row[col[("x", a, c, k)]] = 1.0
            row[col[("qH", j, k)]] = 1.0
            if ("RC", j, k) in col:
                row[col[("RC", j, k)]] = 1.0
            A.append(row); b.append(streams[j].cp * dt)
    for k in range(K - 1):
        row = np.zeros(n); any_term = False
        for i in hs:
            if ("RH", i, k) in col:
                row[col[("RH", i, k)]] += 1.0; any_term = True
        for j in cs:
            if ("RC", j, k + 1) in col:
                row[col[("RC", j, k + 1)]] -= 1.0; any_term = True
        if any_term:
            A.append(row); b.append(0.0)
    c = np.zeros(n)
    for key, idx in col.items():
        if key[0] == "qH":
            c[idx] = 1.0
    res = linprog(c, A_eq=np.array(A), b_eq=np.array(b), bounds=[(0, None)] * n,
                  method="highs")
    return float(res.fun) if res.success else float("nan")

q2 = lp_unmatched_pool_forbidden(STS, DT, MATCHES)
print("  same LP, pool heat barred from unmatched colds : Q_H = " + format(q2, ".6f"))
print()
print(line)
print("VERDICT")
print(line)
if q2 >= 150.0 - 1e-6:
    print("  CONFIRMED. The model's objection is CORRECT and my checker was wrong.")
    print()
    print("  Barring pool heat from a cold stream that no unit touches raises the answer from")
    print("  " + format(r["Q_H"], ".3f") + " to " + format(q2, ".3f") + ", exactly the floor the model computed")
    print("  by hand from C2's duty alone.")
    print()
    print("  Consequence: every minimum-units result in Finding 037 is INVALID, because the")
    print("  networks it found attaining the optimum used the same free pool heat. The")
    print("  refutation of U >= N - 1 was performed against a model that does not describe a")
    print("  realisable network.")
else:
    print("  the pool restriction did not change the answer; the model's objection needs another")
    print("  explanation and the checker stands for now")
