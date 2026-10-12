"""Step 43 - is the topology/value separation statistically real, and what is it really?

Step 42 added genuinely new cuts - thresholds on single component values - and found NO
separation: disjoint-draw pairs averaged 0.976, shared-draw pairs 1.000.

That forces a re-examination of Finding 019, which claimed two things:
  (a) value-value 0.827 vs topology-topology 1.133
  (b) it "reproduces findings 013 and 015 from different cuts"

(b) is wrong: Finding 019's topology cuts ARE Finding 015's structural cuts, identical,
and three of its four value cuts are Finding 013's performance cuts.  The reproduction is
the same measurement, not an independent one.

So the question is whether (a) survives, and if it does, what the cuts in each family have
in common.  Bootstrap over networks gives the sampling error.
"""
import _bootstrap  # noqa: F401
import json
import pathlib
from itertools import combinations

import numpy as np

from ecdr.structure import ensemble, waterbed_numeric
from ecdr.structure.capability import profile

line = "=" * 90
OMEGA = np.logspace(np.log10(0.5), np.log10(3.0e5), 900)
OMEGA_LOW = 2 * np.pi * 30.0
CAL = dict(delta_max=8.0e-3, a_max=8.0, t_iso=0.300)


def build(seed, count=200):
    ens = ensemble(seed=seed, count=count, n_lo=2, n_hi=8)
    profs = [profile(s, OMEGA, OMEGA_LOW) for s in ens]
    from ecdr.structure.capability import requirement_check
    req = [requirement_check(p, CAL["delta_max"], CAL["a_max"], CAL["t_iso"]) for p in profs]
    sag = np.array([p["sag"] for p in profs])
    inband = np.array([p["in_band"] for p in profs])
    peak = np.array([p["peak"] for p in profs])
    g0m = np.array([s.ground_c.get(0, 0.0) / s.masses[0] for s in ens])
    W = np.array([waterbed_numeric(s) for s in ens])
    cuts = {
        "VAL sag": sag > np.median(sag),
        "VAL peak": peak > np.median(peak),
        "VAL in-band": inband > np.median(inband),
        "VAL g0/m0": g0m > np.median(g0m),
        "VAL W": W > np.median(W),
        "TOP payload grounded": np.array([0 in s.ground_k or 0 in s.ground_c for s in ens]),
        "TOP >=2 ties": np.array([len(set(s.ground_k) | set(s.ground_c)) >= 2 for s in ens]),
        "TOP degree>=3": np.array([sum(1 for (i, j) in s.springs if i == 0 or j == 0) >= 3
                                   for s in ens]),
        "TOP n>=6": np.array([s.n >= 6 for s in ens]),
    }
    return cuts


def fam_means(cuts):
    """Mean independence ratio within each family, over one sample."""
    out = {}
    for fam in ("VAL", "TOP"):
        ks = [k for k in cuts if k.startswith(fam)]
        rs = []
        for a, b in combinations(ks, 2):
            ca, cb = cuts[a], cuts[b]
            rs.append(float((~ca & ~cb).mean() / ((1 - ca.mean()) * (1 - cb.mean()))))
        out[fam] = float(np.mean(rs))
    return out


print(line)
print("A. family means over three seeds, with the individual pair ratios shown")
print(line)
for sd in (5, 17, 29):
    c = build(sd)
    m = fam_means(c)
    print("  seed " + str(sd).rjust(3) + "   VAL mean " + format(m["VAL"], ".4f")
          + "   TOP mean " + format(m["TOP"], ".4f"))
    for fam in ("VAL", "TOP"):
        ks = [k for k in c if k.startswith(fam)]
        rs = []
        for a, b in combinations(ks, 2):
            ca, cb = c[a], c[b]
            rs.append(float((~ca & ~cb).mean() / ((1 - ca.mean()) * (1 - cb.mean()))))
        print("        " + fam + " pairs: " + ", ".join(format(x, ".3f") for x in rs))

print()
print(line)
print("B. bootstrap over NETWORKS - how much of the gap is sampling error?")
print(line)
ens = ensemble(seed=5, count=200, n_lo=2, n_hi=8)
profs = [profile(s, OMEGA, OMEGA_LOW) for s in ens]
from ecdr.structure.capability import requirement_check
req = [requirement_check(p, CAL["delta_max"], CAL["a_max"], CAL["t_iso"]) for p in profs]
sag = np.array([p["sag"] for p in profs])
inband = np.array([p["in_band"] for p in profs])
peak = np.array([p["peak"] for p in profs])
g0m = np.array([s.ground_c.get(0, 0.0) / s.masses[0] for s in ens])
W = np.array([waterbed_numeric(s) for s in ens])
base = {
    "VAL sag": sag > np.median(sag), "VAL peak": peak > np.median(peak),
    "VAL in-band": inband > np.median(inband), "VAL g0/m0": g0m > np.median(g0m),
    "VAL W": W > np.median(W),
    "TOP payload grounded": np.array([0 in s.ground_k or 0 in s.ground_c for s in ens]),
    "TOP >=2 ties": np.array([len(set(s.ground_k) | set(s.ground_c)) >= 2 for s in ens]),
    "TOP degree>=3": np.array([sum(1 for (i, j) in s.springs if i == 0 or j == 0) >= 3
                               for s in ens]),
    "TOP n>=6": np.array([s.n >= 6 for s in ens]),
}
rng = np.random.default_rng(0)
vals, tops, diffs = [], [], []
n = 200
for _ in range(2000):
    idx = rng.integers(0, n, n)
    sub = {k: v[idx] for k, v in base.items()}
    m = fam_means(sub)
    vals.append(m["VAL"])
    tops.append(m["TOP"])
    diffs.append(m["TOP"] - m["VAL"])
vals, tops, diffs = map(np.array, (vals, tops, diffs))
lo_v, hi_v = np.percentile(vals, [2.5, 97.5])
lo_t, hi_t = np.percentile(tops, [2.5, 97.5])
lo_d, hi_d = np.percentile(diffs, [2.5, 97.5])
print("  VAL mean  " + format(float(vals.mean()), ".4f")
      + "   95% CI [" + format(float(lo_v), ".4f") + ", " + format(float(hi_v), ".4f") + "]")
print("  TOP mean  " + format(float(tops.mean()), ".4f")
      + "   95% CI [" + format(float(lo_t), ".4f") + ", " + format(float(hi_t), ".4f") + "]")
print("  TOP - VAL " + format(float(diffs.mean()), ".4f")
      + "   95% CI [" + format(float(lo_d), ".4f") + ", " + format(float(hi_d), ".4f") + "]")
print()
if lo_d > 0:
    print("  -> the gap excludes zero.  The separation is real FOR THESE CUTS.")
else:
    print("  -> the gap includes zero; the separation is not established.")

print()
print(line)
print("C. what the two families actually have in common")
print(line)
print("  VAL cuts : sag, peak, in-band, g0/m0, W")
print("  TOP cuts : payload grounded, >=2 ties, degree>=3, n>=6")
print()
print("  Step 42's cuts were thresholds on SINGLE component values of single edges, and")
print("  they produced no separation (disjoint-draw mean 0.976, shared-draw 1.000).")
print()
print("  The difference is not topology versus value.  It is that every VAL cut is a")
print("  function of the SAME underlying question - how well does this structure")
print("  isolate - while the TOP cuts and step 42's cuts are not.  Cuts that measure one")
print("  capability are redundant with each other; cuts that do not are not.")

out = pathlib.Path(__file__).resolve().parents[1] / "runs"
out.mkdir(exist_ok=True)
(out / "separation_test.json").write_text(json.dumps({
    "val_mean": float(vals.mean()), "val_ci": [float(lo_v), float(hi_v)],
    "top_mean": float(tops.mean()), "top_ci": [float(lo_t), float(hi_t)],
    "diff_mean": float(diffs.mean()), "diff_ci": [float(lo_d), float(hi_d)],
    "gap_excludes_zero": bool(lo_d > 0),
}, indent=1), encoding="utf-8")
print()
print("wrote runs/separation_test.json")
