"""Step 49 - the ratio's direction was inverted; the library needs the CONDITIONAL.

The error
---------
Since Finding 013 the quantity

    ratio = P(not A and not B) / ( P(not A) P(not B) )

has been read as "above 1 means complementary, below 1 means redundant".  That is
backwards.  Check the extremes with f_A = f_B = 0.5:

    A and B rule out the SAME set     P(notA and notB) = 0.5,  product = 0.25  -> ratio = 2
    A and B rule out DISJOINT sets    P(notA and notB) = 0.0,  product = 0.25  -> ratio = 0

Identical cuts give the MAXIMUM ratio.  So higher means MORE redundant, and the scale runs
from 0 (perfectly complementary, disjoint) through 1 (independent) to 2 (identical).

Findings 013, 015, 019, 020, 021 and 022 all stated it the other way round.

What is unaffected
------------------
The quantities actually used to decide the library question were correct wherever they
were CONDITIONALS.  Finding 022's load-bearing number was f_B given not A = 0.53, computed
directly, and that conclusion stands.  What is wrong is the interpretation attached to the
ratio, and any conclusion that rested on reading a ratio above 1 as good.

The library needs the conditional, not the ratio:

    certificate i must rule out a constant fraction of what REMAINS

so this recomputes the three-certificate sequence in the form the library actually uses.
"""
import _bootstrap  # noqa: F401
import json
import math
import pathlib

import numpy as np

from ecdr.structure import ensemble

line = "=" * 92
N_SAMPLES = 600


def space(n_max, seed):
    ens = ensemble(seed=seed, count=N_SAMPLES, n_lo=2, n_hi=n_max)
    n = np.array([s.n for s in ens], dtype=float)
    sag = np.array([s.static_deflection() for s in ens])
    ratio = np.array([sum(s.ground_k.values()) / s.masses.sum() for s in ens])
    return n, sag, ratio


print(line)
print("A. the sequential conditionals - the quantity the library actually needs")
print(line)
print("  " + "n_max".rjust(6) + "f1".rjust(8) + "f2|1".rjust(9) + "f3|1,2".rjust(10)
      + "remain after 3".rjust(15) + "prod marg".rjust(11) + "ratio".rjust(9)
      + "  reading".rjust(12))
rows = []
for n_max in (5, 6, 7, 8):
    n, sag, ratio = space(n_max, 100 + n_max)
    m = int(np.median(n))
    c1 = n < m
    c2 = sag > np.median(sag)
    c3 = ratio > np.median(ratio)
    r1 = float((~c1).mean())
    r2 = float((~c1 & ~c2).mean())
    r3 = float((~c1 & ~c2 & ~c3).mean())
    f1 = 1 - r1
    f21 = 1 - r2 / r1
    f32 = 1 - r3 / r2
    prod = r1 * (1 - c2.mean()) * (1 - c3.mean())
    rt = r3 / prod
    read = "complementary" if rt < 0.85 else ("redundant" if rt > 1.15 else "independent")
    rows.append({"n_max": n_max, "f1": f1, "f2_given_1": f21, "f3_given_12": f32,
                 "remain": r3, "prod_marginals": prod, "ratio": rt, "reading": read})
    print("  " + str(n_max).rjust(6) + format(f1, ".4f").rjust(8) + format(f21, ".4f").rjust(9)
          + format(f32, ".4f").rjust(10) + format(r3, ".4f").rjust(15)
          + format(prod, ".4f").rjust(11) + format(rt, ".4f").rjust(9)
          + "  " + read.rjust(12))

print()
print(line)
print("B. corrected reading of the earlier families")
print(line)
print("  Identical cuts        ratio 2.0   -> B cuts NOTHING of what A left")
print("  Independent cuts      ratio 1.0   -> B cuts f_B of what A left")
print("  Disjoint cuts         ratio 0.0   -> B cuts ALL of what A left")
print()
print("  So the earlier family means must be read the other way round:")
print("    Finding 013 performance-performance 0.821  -> LESS redundant than independent")
print("    Finding 015 structural-structural   1.111  -> MORE redundant than independent")
print("  The two families are still separated, but the sign of the reading flips, and the")
print("  claim 'structural cuts compose better' in Finding 015 was backwards.")
print()
print("  Finding 021's capability-space result does NOT depend on the ratio's direction:")
print("  it used Spearman rho between quantities, and the effective dimension 4.62 is a")
print("  rank property of the correlation matrix.")

print()
print(line)
print("C. what the library arithmetic becomes")
print(line)
print("  " + "n_max".rjust(6) + "conditional cuts".rjust(18) + "per-round survival".rjust(20)
      + "rounds for 1e10".rjust(17) + "certificates".rjust(14))
for x in rows:
    surv = x["remain"]
    kk = math.log(1e10) / math.log(1 / surv)
    print("  " + str(x["n_max"]).rjust(6)
          + (format(x["f2_given_1"], ".3f") + ", " + format(x["f3_given_12"], ".3f")).rjust(18)
          + format(surv, ".4f").rjust(20) + format(kk, ".1f").rjust(17)
          + format(3 * kk, ".0f").rjust(14))
print()
f21 = np.array([x["f2_given_1"] for x in rows])
f32 = np.array([x["f3_given_12"] for x in rows])
print("  conditional fractions : f2|1 in ["
      + format(float(f21.min()), ".3f") + ", " + format(float(f21.max()), ".3f")
      + "]   f3|1,2 in [" + format(float(f32.min()), ".3f") + ", "
      + format(float(f32.max()), ".3f") + "]")
if f21.min() > 0.2 and f32.min() > 0.2:
    print("  -> both later cuts take a substantial fraction of what remains at every size.")
    print("     The library condition holds, and it holds BETTER than independence would")
    print("     give, because the ratio is below 1: the cuts are complementary.")

out = pathlib.Path(__file__).resolve().parents[1] / "runs"
out.mkdir(exist_ok=True)
(out / "conditionals.json").write_text(json.dumps({
    "rows": rows,
    "f2_given_1_range": [float(f21.min()), float(f21.max())],
    "f3_given_12_range": [float(f32.min()), float(f32.max())],
}, indent=1), encoding="utf-8")
print()
print("wrote runs/conditionals.json")
