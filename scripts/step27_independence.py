"""Step 27 - independence of STRUCTURAL cuts vs PERFORMANCE cuts.

Finding 013 measured that the three performance axes compose at an independence ratio of
0.437 (failures cluster).  It concluded that independent coverage must come from
certificates keyed to different STRUCTURAL features.  That conclusion was a prescription,
not a measurement.

This measures it.  For each candidate cut - structural or performance - take the set of
structures it rules out, and compute pairwise:

    observed joint survival / product of marginal survivals

1.0 means independent, < 1 means the cuts overlap more than chance (redundant), > 1 means
they are complementary.

NOTE ON STATUS: the structural predicates here are NOT certificates. No sound bound has
been proved along them yet. What is measured is whether a certificate found along each
axis WOULD compose, which is the precondition for looking there at all.
"""
import _bootstrap  # noqa: F401
import json
import pathlib
from itertools import combinations

import numpy as np

from ecdr.structure import ensemble
from ecdr.structure.capability import profile, requirement_check

line = "=" * 90
N_STRUCT = 600
OMEGA = np.logspace(np.log10(0.5), np.log10(3.0e5), 900)
OMEGA_LOW = 2 * np.pi * 30.0
CAL = dict(delta_max=8.0e-3, a_max=8.0, t_iso=0.300)

SEEDS = [5, 17, 29]


def build(seed):
    e = ensemble(seed=seed, count=N_STRUCT, n_lo=2, n_hi=8)
    p = [profile(s, OMEGA, OMEGA_LOW) for s in e]
    r = [requirement_check(q, CAL["delta_max"], CAL["a_max"], CAL["t_iso"]) for q in p]
    c = {}
    c["PERF: sag"] = np.array([x["sag"] for x in r])
    c["PERF: peak"] = np.array([x["peak"] for x in r])
    c["PERF: in-band"] = np.array([x["band"] for x in r])
    c["STR: payload grounded"] = np.array([0 in s.ground_k or 0 in s.ground_c for s in e])
    c["STR: >=2 ground ties"] = np.array(
        [len(set(s.ground_k) | set(s.ground_c)) >= 2 for s in e])
    c["STR: payload degree>=3"] = np.array(
        [sum(1 for (i, j) in s.springs if i == 0 or j == 0) >= 3 for s in e])
    c["STR: n >= 6"] = np.array([s.n >= 6 for s in e])
    return c


ens = ensemble(seed=5, count=N_STRUCT, n_lo=2, n_hi=8)
profs = [profile(s, OMEGA, OMEGA_LOW) for s in ens]
req = [requirement_check(p, CAL["delta_max"], CAL["a_max"], CAL["t_iso"]) for p in profs]

cuts = {}
cuts["PERF: sag"] = np.array([r["sag"] for r in req])
cuts["PERF: peak"] = np.array([r["peak"] for r in req])
cuts["PERF: in-band"] = np.array([r["band"] for r in req])
cuts["STR: payload grounded"] = np.array([0 in s.ground_k or 0 in s.ground_c for s in ens])
cuts["STR: >=2 ground ties"] = np.array([len(set(s.ground_k) | set(s.ground_c)) >= 2 for s in ens])
cuts["STR: payload degree>=3"] = np.array(
    [sum(1 for (i, j) in s.springs if i == 0 or j == 0) >= 3 for s in ens])
cuts["STR: n >= 6"] = np.array([s.n >= 6 for s in ens])

print(line)
print("A. individual cuts")
print(line)
print("  " + "cut".rjust(26) + "rules out".rjust(11) + "fraction".rjust(11))
for k, v in cuts.items():
    print("  " + k.rjust(26) + str(int(v.sum())).rjust(11)
          + format(v.mean(), ".4f").rjust(11))


def ratio(a, b):
    """observed joint survival over product of marginal survivals."""
    pa, pb = 1 - a.mean(), 1 - b.mean()
    both = (~a & ~b).mean()
    if pa <= 0 or pb <= 0:
        return float("nan"), float("nan"), float("nan")
    return both / (pa * pb), pa, pb


keys = list(cuts)
print()
print(line)
print("B. pairwise independence ratio (1.0 = independent, <1 = redundant)")
print(line)
print("  " + "pair".rjust(46) + "ratio".rjust(9) + "jaccard".rjust(10) + "kind".rjust(14))
rows = []
for a, b in combinations(keys, 2):
    r, pa, pb = ratio(cuts[a], cuts[b])
    inter = (cuts[a] & cuts[b]).sum()
    union = (cuts[a] | cuts[b]).sum()
    jac = inter / union if union else 0.0
    def fam(k):
        return k.split(":")[0]
    kind = ("structural-structural" if fam(a) == fam(b) == "STR"
            else "performance-performance" if fam(a) == fam(b) == "PERF"
            else "cross")
    rows.append({"a": a, "b": b, "ratio": r, "jaccard": jac, "kind": kind})
    print("  " + (a + "  x  " + b).rjust(46) + format(r, ".4f").rjust(9)
          + format(jac, ".4f").rjust(10) + kind.rjust(14))

print()
print(line)
print("C. VERDICT - are structural cuts more independent than performance cuts?")
print(line)
for kind in ("performance-performance", "structural-structural", "cross"):
    vals = [r["ratio"] for r in rows if r["kind"] == kind and np.isfinite(r["ratio"])]
    if vals:
        print("  " + kind.rjust(26) + " mean ratio " + format(float(np.mean(vals)), ".4f")
              + "   median " + format(float(np.median(vals)), ".4f")
              + "   n = " + str(len(vals)))
print()
ss = [r["ratio"] for r in rows if r["kind"] == "structural-structural" and np.isfinite(r["ratio"])]
pp = [r["ratio"] for r in rows if r["kind"] == "performance-performance" and np.isfinite(r["ratio"])]
if ss and pp:
    ms, mp = float(np.mean(ss)), float(np.mean(pp))
    print("  structural mean " + format(ms, ".4f") + "  vs  performance mean " + format(mp, ".4f"))
    if ms > mp * 1.15:
        print("  -> Finding 013's prescription is CONFIRMED: structural cuts are")
        print("     meaningfully more independent than performance cuts.")
    elif ms < mp * 0.85:
        print("  -> Finding 013's prescription is REFUTED on this ensemble: structural")
        print("     cuts are MORE redundant than performance cuts.")
    else:
        print("  -> no meaningful difference on this ensemble.  The prescription is")
        print("     not supported by this measurement, and the ground-coupling axes in")
        print("     particular may be measuring the same underlying property.")

print()
print(line)
print("D. ROBUSTNESS - the same comparison over three independent ensembles")
print(line)
print("  " + "seed".rjust(6) + "perf-perf".rjust(12) + "struct-struct".rjust(15)
      + "cross".rjust(10) + "  verdict".rjust(12))
multi = []
for sd in SEEDS:
    c2 = build(sd)
    ks = list(c2)
    acc = {}
    for a, b in combinations(ks, 2):
        rr, _, _ = ratio(c2[a], c2[b])
        fa = a.split(":")[0]
        fb = b.split(":")[0]
        kd = ("structural-structural" if fa == fb == "STR"
              else "performance-performance" if fa == fb == "PERF" else "cross")
        acc.setdefault(kd, []).append(rr)
    m = {k: float(np.mean(v)) for k, v in acc.items()}
    multi.append({"seed": sd, **m})
    verdict = "CONFIRMED" if m["structural-structural"] > m["performance-performance"] else "not confirmed"
    print("  " + str(sd).rjust(6) + format(m["performance-performance"], ".4f").rjust(12)
          + format(m["structural-structural"], ".4f").rjust(15)
          + format(m["cross"], ".4f").rjust(10) + "  " + verdict.rjust(12))
pp_all = [m["performance-performance"] for m in multi]
ss_all = [m["structural-structural"] for m in multi]
print()
print("  performance-performance mean over seeds: " + format(float(np.mean(pp_all)), ".4f"))
print("  structural-structural   mean over seeds: " + format(float(np.mean(ss_all)), ".4f"))
print("  every seed in the same direction: "
      + str(all(s > p for s, p in zip(ss_all, pp_all))))
print()
print("  CAVEAT: each seed contributes only 3 performance-performance pairs and 6")
print("  structural-structural pairs, so the separation rests on few pairs.  Three")
print("  seeds agreeing on the DIRECTION is the evidence, not a significance test.")

out = pathlib.Path(__file__).resolve().parents[1] / "runs"
out.mkdir(exist_ok=True)
(out / "independence.json").write_text(json.dumps({
    "cut_sizes": {k: int(v.sum()) for k, v in cuts.items()},
    "pairs": rows, "multi_seed": multi,
}, indent=1, default=str), encoding="utf-8")
print()
print("wrote runs/independence.json")
