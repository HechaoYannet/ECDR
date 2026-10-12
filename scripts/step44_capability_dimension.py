"""Step 44 - how many independent axes does the capability space actually have?

Finding 020 concluded that every performance cut is a monotone function of one scalar, and
that this is a threat to the whole library programme, because Finding 011 needs successive
cuts to take a constant fraction of what remains.

That claim is testable in one shot.  Take a set of sound bounds and structural quantities,
standardise them, and look at the eigenvalue spectrum of their correlation matrix:

    one dominant eigenvalue      -> one scalar, no independent certificates exist,
                                    and the programme needs redesigning rather than
                                    more searching
    participation ratio of 3-4   -> several axes, and the search should continue

The participation ratio is (sum L)^2 / sum L^2, i.e. the effective number of independent
directions.  It is reported alongside the fraction of variance in the leading eigenvalue.
"""
import _bootstrap  # noqa: F401
import json
import pathlib

import numpy as np

from ecdr.structure import ensemble, waterbed_numeric
from ecdr.structure.capability import profile

line = "=" * 90
OMEGA = np.logspace(np.log10(0.5), np.log10(3.0e5), 900)
OMEGA_LOW = 2 * np.pi * 30.0

ens = ensemble(seed=5, count=300, n_lo=2, n_hi=8)
profs = [profile(s, OMEGA, OMEGA_LOW) for s in ens]

Q = {}
Q["sag"] = np.array([p["sag"] for p in profs])
Q["W waterbed"] = np.array([waterbed_numeric(s) for s in ens])
Q["g0/m0 high-freq"] = np.array([s.ground_c.get(0, 0.0) / s.masses[0] for s in ens])
Q["n components"] = np.array([float(s.n) for s in ens])
Q["n ground ties"] = np.array([float(len(set(s.ground_k) | set(s.ground_c))) for s in ens])
Q["total mass"] = np.array([float(s.masses.sum()) for s in ens])
Q["total ground k"] = np.array([float(sum(s.ground_k.values())) for s in ens])
Q["peak |T|"] = np.array([p["peak"] for p in profs])
Q["in-band |T|"] = np.array([p["in_band"] for p in profs])
Q["payload degree"] = np.array([float(sum(1 for (i, j) in s.springs if i == 0 or j == 0))
                                for s in ens])
Q["mean degree"] = np.array([2.0 * len(s.springs) / s.n for s in ens])
Q["total damping"] = np.array([float(sum(s.dampers.values()) + sum(s.ground_c.values()))
                               for s in ens])

names = list(Q)
X = np.column_stack([Q[k] for k in names])
# rank-standardise: heavy tails and different units make Pearson useless here
R = np.column_stack([np.argsort(np.argsort(X[:, j])).astype(float) for j in range(X.shape[1])])
R = (R - R.mean(0)) / R.std(0)
C = np.corrcoef(R.T)

ev = np.sort(np.linalg.eigvalsh(C))[::-1]
pr = float(ev.sum() ** 2 / (ev ** 2).sum())

print(line)
print("A. the quantities")
print(line)
print("  " + "quantity".rjust(20) + "p10".rjust(13) + "median".rjust(13) + "p90".rjust(13))
for k in names:
    p10, p50, p90 = np.percentile(Q[k], [10, 50, 90])
    print("  " + k.rjust(20) + format(p10, ".4g").rjust(13) + format(p50, ".4g").rjust(13)
          + format(p90, ".4g").rjust(13))

print()
print(line)
print("B. pairwise rank correlation - how many pairs are near zero?")
print(line)
pairs = []
for i in range(len(names)):
    for j in range(i + 1, len(names)):
        pairs.append((names[i], names[j], float(C[i, j])))
absr = np.array([abs(p[2]) for p in pairs])
print("  pairs : " + str(len(pairs)))
for thr in (0.1, 0.2, 0.3, 0.5):
    print("  |rho| < " + format(thr, ".1f").rjust(4) + " : "
          + str(int((absr < thr).sum())).rjust(3) + " of " + str(len(pairs)))
print("  median |rho| = " + format(float(np.median(absr)), ".4f"))
print()
print("  the five least correlated pairs:")
for a, b, r in sorted(pairs, key=lambda t: abs(t[2]))[:5]:
    print("    " + (a + "  x  " + b).ljust(40) + format(r, "+.4f").rjust(9))
print("  the five most correlated pairs:")
for a, b, r in sorted(pairs, key=lambda t: -abs(t[2]))[:5]:
    print("    " + (a + "  x  " + b).ljust(40) + format(r, "+.4f").rjust(9))

print()
print(line)
print("C. the eigenvalue spectrum")
print(line)
print("  " + "component".rjust(5) + "eigenvalue".rjust(14) + "share of variance".rjust(20)
      + "cumulative".rjust(14))
cum = 0.0
for i, v in enumerate(ev):
    cum += v
    print("  " + str(i + 1).rjust(5) + format(v, ".4f").rjust(14)
          + format(v / ev.sum(), ".4f").rjust(20) + format(cum / ev.sum(), ".4f").rjust(14))
print()
print("  participation ratio (effective number of axes) : " + format(pr, ".3f"))
print("  leading eigenvalue share                       : " + format(ev[0] / ev.sum(), ".4f"))
print("  components needed for 90 percent of variance   : "
      + str(int(np.searchsorted(np.cumsum(ev) / ev.sum(), 0.90) + 1)))

print()
print(line)
print("D. VERDICT")
print(line)
if ev[0] / ev.sum() > 0.75:
    print("  ONE DOMINANT AXIS.  The capability space is effectively one-dimensional, so")
    print("  no two performance cuts can be independent, and the library programme as")
    print("  specified cannot work.  The programme needs redesigning, not more searching.")
elif pr >= 3.0:
    print("  MULTIPLE AXES.  The effective dimension is " + format(pr, ".1f")
          + ", so independent certificates are not ruled out by the structure of the")
    print("  capability space.  The search should continue, and Finding 020's reading was")
    print("  too pessimistic - it was measuring a SET of cuts all chosen on one axis.")
else:
    print("  INTERMEDIATE.  Effective dimension " + format(pr, ".1f")
          + "; leading share " + format(ev[0] / ev.sum(), ".3f") + ".")

out = pathlib.Path(__file__).resolve().parents[1] / "runs"
out.mkdir(exist_ok=True)
(out / "capability_dimension.json").write_text(json.dumps({
    "names": names,
    "eigenvalues": [float(v) for v in ev],
    "participation_ratio": pr,
    "leading_share": float(ev[0] / ev.sum()),
    "least_correlated": [{"a": a, "b": b, "rho": r}
                         for a, b, r in sorted(pairs, key=lambda t: abs(t[2]))[:8]],
}, indent=1), encoding="utf-8")
print()
print("wrote runs/capability_dimension.json")
