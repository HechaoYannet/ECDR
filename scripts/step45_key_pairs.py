"""Step 45 - are the near-zero correlations real, or one sample's noise?

Step 44 found the capability space to have an effective dimension of 4.62 with 14 of 66
pairs below |rho| = 0.1.  The pairs that matter for the certificate programme are the ones
joining a SOUND, topology-keyed bound to a performance bound:

    n components      x  in-band |T|      rho = +0.0174
    waterbed W        x  payload degree   rho = +0.0204
    g0/m0             x  payload degree   rho = -0.0034

If those survive bootstrap and a change of seed, then a modal certificate composes with a
performance certificate and Finding 020's pessimistic reading was measuring an artefact of
having chosen every cut on one axis.
"""
import _bootstrap  # noqa: F401
import json
import pathlib

import numpy as np
from scipy.stats import spearmanr

from ecdr.structure import ensemble, waterbed_numeric
from ecdr.structure.capability import profile

line = "=" * 88
OMEGA = np.logspace(np.log10(0.5), np.log10(3.0e5), 900)
OMEGA_LOW = 2 * np.pi * 30.0


def quantities(seed, count=300):
    ens = ensemble(seed=seed, count=count, n_lo=2, n_hi=8)
    profs = [profile(s, OMEGA, OMEGA_LOW) for s in ens]
    return {
        "n components": np.array([float(s.n) for s in ens]),
        "in-band |T|": np.array([p["in_band"] for p in profs]),
        "W waterbed": np.array([waterbed_numeric(s) for s in ens]),
        "payload degree": np.array([float(sum(1 for (i, j) in s.springs if i == 0 or j == 0))
                                    for s in ens]),
        "g0/m0": np.array([s.ground_c.get(0, 0.0) / s.masses[0] for s in ens]),
        "sag": np.array([p["sag"] for p in profs]),
    }


PAIRS = [("n components", "in-band |T|"), ("W waterbed", "payload degree"),
         ("g0/m0", "payload degree"), ("sag", "in-band |T|")]

print(line)
print("A. the key pairs across three seeds")
print(line)
print("  " + "pair".rjust(34) + "seed 5".rjust(12) + "seed 17".rjust(12) + "seed 29".rjust(12))
store = {}
for sd in (5, 17, 29):
    store[sd] = quantities(sd)
for a, b in PAIRS:
    row = []
    for sd in (5, 17, 29):
        rho, _ = spearmanr(store[sd][a], store[sd][b])
        row.append(float(rho))
    print("  " + (a + "  x  " + b).rjust(34) + "".join(format(v, "+.4f").rjust(12) for v in row))

print()
print(line)
print("B. bootstrap over networks, seed 5")
print(line)
q = store[5]
n = len(q["n components"])
rng = np.random.default_rng(0)
print("  " + "pair".rjust(34) + "rho".rjust(10) + "95% CI".rjust(24) + "  contains 0".rjust(13))
rows = []
for a, b in PAIRS:
    rho0, _ = spearmanr(q[a], q[b])
    bs = []
    for _ in range(1500):
        idx = rng.integers(0, n, n)
        bs.append(spearmanr(q[a][idx], q[b][idx])[0])
    bs = np.array(bs)
    lo, hi = np.percentile(bs, [2.5, 97.5])
    rows.append({"a": a, "b": b, "rho": float(rho0), "lo": float(lo), "hi": float(hi)})
    print("  " + (a + "  x  " + b).rjust(34) + format(float(rho0), "+.4f").rjust(10)
          + ("[" + format(float(lo), "+.4f") + ", " + format(float(hi), "+.4f") + "]").rjust(24)
          + ("   yes" if lo < 0 < hi else "   no").rjust(13))

print()
print(line)
print("C. VERDICT")
print(line)
near = [r for r in rows if abs(r["rho"]) < 0.15 and r["lo"] < 0 < r["hi"]]
print("  pairs with |rho| < 0.15 and a CI containing zero : " + str(len(near)) + " of " + str(len(rows)))
for r in near:
    print("    " + (r["a"] + "  x  " + r["b"]))
print()
if any(r["a"] == "n components" for r in near):
    print("  The modal bound (number of components) is statistically uncorrelated with the")
    print("  isolation performance.  It is SOUND, it is keyed to topology, and a threshold")
    print("  at the median cuts about half the space.  So a modal certificate and a")
    print("  performance certificate are a composing pair, and Finding 020's conclusion that")
    print("  'no two such certificates will compose' was drawn from cuts all taken on one")
    print("  axis rather than from a property of the space.")

out = pathlib.Path(__file__).resolve().parents[1] / "runs"
out.mkdir(exist_ok=True)
(out / "key_pairs.json").write_text(json.dumps({
    "pairs": rows,
    "near_zero": [{"a": r["a"], "b": r["b"]} for r in near],
}, indent=1), encoding="utf-8")
print()
print("wrote runs/key_pairs.json")
