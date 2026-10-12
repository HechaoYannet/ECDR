"""Step 47 - the TIME-SCALE family: derive and verify a sound bound.

Roadmap section 6 lists four candidate invariant families.  Findings 010 and 022 settled
the modal family; Finding 018 settled the band-tradeoff family; the energy/passivity family
is degenerate (its predicate is a property of the REQUIREMENT, so its coverage is 0 or 1).
The time-scale family is still open.

The bound
---------
For a mechanical network, K 1 = f, where f_i is the ground stiffness at node i.  The
Rayleigh quotient of the trial vector 1 is therefore

    (1^T K 1) / (1^T M 1)  =  (sum of ground stiffnesses) / (sum of masses)

and the Rayleigh principle gives, for the SMALLEST natural frequency,

    omega_1^2  <=  (sum_ground k) / (sum m)

This is sound for EVERY parameter assignment, it costs O(n) to evaluate, and it is keyed
to a different mechanism from mode counting: the mass-to-stiffness ratio, not the number of
components.  A requirement that the structure respond slowly, omega_1 <= omega_max, is
therefore refuted cheaply whenever the ratio exceeds omega_max^2.

Verification: compare against the true smallest generalised eigenvalue of (K, M).
"""
import _bootstrap  # noqa: F401
import json
import pathlib

import numpy as np

from ecdr.structure import ensemble

line = "=" * 88
ens = ensemble(seed=5, count=300, n_lo=2, n_hi=8)


def true_omega1_sq(s):
    M, C, K, f, g = s.matrices()
    Minv = np.diag(1.0 / np.diag(M))
    A = Minv @ K
    ev = np.linalg.eigvals(A)
    ev = np.sort(ev.real)
    return float(ev[0])


def rayleigh_bound(s):
    M, C, K, f, g = s.matrices()
    return float(f.sum() / s.masses.sum())


rows = []
for i, s in enumerate(ens):
    t = true_omega1_sq(s)
    b = rayleigh_bound(s)
    rows.append({"i": i, "n": s.n, "true": t, "bound": b,
                 "ratio": t / b if b > 0 else float("nan")})
ratio = np.array([r["ratio"] for r in rows])

print(line)
print("A. is the Rayleigh bound sound?  true omega_1^2 / bound must be <= 1")
print(line)
print("  structures tested          : " + str(len(rows)))
print("  max ratio true/bound       : " + format(float(ratio.max()), ".6f"))
print("  min ratio                  : " + format(float(ratio.min()), ".6f"))
print("  median ratio               : " + format(float(np.median(ratio)), ".6f"))
viol = int((ratio > 1.0 + 1e-9).sum())
print("  VIOLATIONS (ratio > 1)     : " + str(viol))
print()
if viol == 0:
    print("  -> the bound holds on every network.  Rayleigh's principle applies to any")
    print("     trial vector and 1 is admissible because K 1 = f.")
print()
print("  tightness: the bound exceeds the true value by a factor of")
print("    " + format(float(np.median(1.0 / np.maximum(ratio, 1e-12))), ".3f") + " at the median")

print()
print(line)
print("B. what it is keyed to")
print(line)
gsum = np.array([sum(s.ground_k.values()) for s in ens])
msum = np.array([s.masses.sum() for s in ens])
n = np.array([s.n for s in ens])
from scipy.stats import spearmanr
for tag, v in (("n components", n), ("payload degree",
                                    np.array([sum(1 for (i, j) in s.springs
                                                  if i == 0 or j == 0) for s in ens]))):
    rho, p = spearmanr(ratio, v)
    print("  rank corr of true/bound tightness with " + tag.ljust(16)
          + format(float(rho), "+.4f").rjust(9) + "   p = " + format(float(p), ".2e"))
rho_b, _ = spearmanr(np.array([r["bound"] for r in rows]), n)
print("  rank corr of the BOUND itself with n components : " + format(float(rho_b), "+.4f"))
print()
print("  A bound whose value is uncorrelated with the modal count is a candidate for a")
print("  library member independent of the modal certificate.")

out = pathlib.Path(__file__).resolve().parents[1] / "runs"
out.mkdir(exist_ok=True)
(out / "rayleigh_bound.json").write_text(json.dumps({
    "max_ratio": float(ratio.max()), "min_ratio": float(ratio.min()),
    "median_ratio": float(np.median(ratio)), "violations": viol,
    "median_tightness": float(np.median(1.0 / np.maximum(ratio, 1e-12))),
    "rho_bound_vs_n": float(rho_b),
}, indent=1), encoding="utf-8")
print()
print("wrote runs/rayleigh_bound.json")
