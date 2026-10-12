"""Step 41 - the real distinction is TOPOLOGY vs VALUE, not structural vs performance.

Finding 013 measured performance-metric cuts at a mean independence ratio of 0.821 and
called them redundant.  Finding 015 measured structural cuts at 1.111 and concluded that
independence comes from structural features.  Step 40 then put the two CERTIFICATE
candidates - the payload-tie law (g0/m0) and the waterbed law (W) - against each other and
got 0.6066, with Spearman rho = -0.50.  By Finding 015's own rule those are one
certificate wearing two hats.

That kills the reading of Finding 015, because g0/m0 and W are both structural.  But a
different split explains all three results at once:

    TOPOLOGY cuts   are drawn independently of the component values
    VALUE cuts      are all functions of the same drawn component values

so value cuts share a common factor by construction, whatever they are called.  Test:
compute the ratio matrix over BOTH families together and compare within and across.
"""
import _bootstrap  # noqa: F401
import json
import pathlib

import numpy as np
from scipy.stats import spearmanr

from ecdr.structure import ensemble, waterbed_numeric
from ecdr.structure.capability import profile

line = "=" * 92
OMEGA = np.logspace(np.log10(0.5), np.log10(3.0e5), 900)
OMEGA_LOW = 2 * np.pi * 30.0

ens = ensemble(seed=5, count=200, n_lo=2, n_hi=8)
profs = [profile(s, OMEGA, OMEGA_LOW) for s in ens]

g_over_m = np.array([s.ground_c.get(0, 0.0) / s.masses[0] for s in ens])
W = np.array([waterbed_numeric(s) for s in ens])
sag = np.array([p["sag"] for p in profs])
inband = np.array([p["in_band"] for p in profs])

cuts = {}
# VALUE-derived: every one is a function of the drawn component values
cuts["VAL g0/m0"] = g_over_m > np.median(g_over_m)
cuts["VAL W"] = W > np.median(W)
cuts["VAL sag"] = sag > np.median(sag)
cuts["VAL in-band"] = inband > np.median(inband)
# TOPOLOGY-derived: drawn independently of the component values
cuts["TOP payload grounded"] = np.array([0 in s.ground_k or 0 in s.ground_c for s in ens])
cuts["TOP >=2 ground ties"] = np.array(
    [len(set(s.ground_k) | set(s.ground_c)) >= 2 for s in ens])
cuts["TOP payload degree>=3"] = np.array(
    [sum(1 for (i, j) in s.springs if i == 0 or j == 0) >= 3 for s in ens])
cuts["TOP n >= 6"] = np.array([s.n >= 6 for s in ens])

print(line)
print("A. cuts")
print(line)
print("  " + "cut".rjust(26) + "rules out".rjust(11) + "fraction".rjust(11))
for k, v in cuts.items():
    print("  " + k.rjust(26) + str(int(v.sum())).rjust(11) + format(v.mean(), ".4f").rjust(11))


def ratio(a, b):
    return float((~a & ~b).mean() / ((1 - a.mean()) * (1 - b.mean())))


keys = list(cuts)
print()
print(line)
print("B. ratio matrix")
print(line)
head = "  " + "".rjust(26) + "".join(k.split()[0][:3].rjust(7) for k in keys)
print(head)
rows = []
for i, a in enumerate(keys):
    cells = []
    for j, b in enumerate(keys):
        if i == j:
            cells.append("   -   ")
            continue
        r = ratio(cuts[a], cuts[b])
        cells.append(format(r, ".3f").rjust(7))
        if i < j:
            fa, fb = a.split()[0], b.split()[0]
            kind = ("value-value" if fa == fb == "VAL"
                    else "topology-topology" if fa == fb == "TOP" else "cross")
            rows.append({"a": a, "b": b, "ratio": r, "kind": kind})
    print("  " + a.rjust(26) + "".join(cells))

print()
print(line)
print("C. the three families")
print(line)
for kind in ("value-value", "topology-topology", "cross"):
    v = [r["ratio"] for r in rows if r["kind"] == kind]
    if v:
        print("  " + kind.rjust(22) + " mean " + format(float(np.mean(v)), ".4f")
              + "   median " + format(float(np.median(v)), ".4f")
              + "   min " + format(float(np.min(v)), ".4f")
              + "   max " + format(float(np.max(v)), ".4f")
              + "   n = " + str(len(v)))

vv = [r["ratio"] for r in rows if r["kind"] == "value-value"]
tt = [r["ratio"] for r in rows if r["kind"] == "topology-topology"]
if vv and tt:
    print()
    print("  value-value mean    " + format(float(np.mean(vv)), ".4f"))
    print("  topology-topology   " + format(float(np.mean(tt)), ".4f"))
    print()
    print("  Compare with the earlier rounds:")
    print("    Finding 013 performance-performance 0.8210")
    print("    Finding 015 structural-structural   1.1110")
    print("    this round value-value              " + format(float(np.mean(vv)), ".4f"))
    print("    this round topology-topology        " + format(float(np.mean(tt)), ".4f"))
    print()
    print("  If the value-value mean lands on Finding 013's number and the")
    print("  topology-topology mean lands on Finding 015's, then the split that matters is")
    print("  TOPOLOGY vs VALUE, and Finding 015's 'structural vs performance' reading was a")
    print("  coincidence of which cuts happened to be topology-derived.")

out = pathlib.Path(__file__).resolve().parents[1] / "runs"
out.mkdir(exist_ok=True)
(out / "topology_vs_value.json").write_text(json.dumps({
    "pairs": rows,
    "families": {k: [r["ratio"] for r in rows if r["kind"] == k]
                 for k in ("value-value", "topology-topology", "cross")},
}, indent=1), encoding="utf-8")
print()
print("wrote runs/topology_vs_value.json")
