"""Step 50 - a fourth sound certificate, and an independent replication.

Part 1  the FAST time scale.  Finding 023 added a bound on the slowest natural frequency
        (Rayleigh with the trial vector 1).  A bound on the FASTEST one comes from the
        infinity norm, which dominates the spectral radius:

            omega_n^2  =  lambda_max(M^-1 K)  <=  max_i ( K_ii + sum_{j != i} |K_ij| ) / m_i
                                             =  max_i ( 2 sum_{j != i} k_ij + k_i^ground ) / m_i

        A requirement needing a response FASTER than the structure can produce is refuted
        whenever the bound is below the required frequency.  That is the opposite side of
        the same physical constraint as the Finding-023 bound, and a genuinely different
        predicate.

Part 2  replication on a DIFFERENT ensemble family - graphs with loops instead of trees,
        uniformly drawn component values instead of log-uniform - and a DIFFERENT
        calibration, at the 30th percentile instead of the median.
"""
import _bootstrap  # noqa: F401
import json
import math
import pathlib

import numpy as np

from ecdr.structure import ensemble

line = "=" * 92
N = 600


def true_omega_max_sq(s):
    M, C, K, f, g = s.matrices()
    A = np.diag(1.0 / np.diag(M)) @ K
    return float(np.sort(np.linalg.eigvals(A).real)[-1])


def fast_bound(s):
    """Infinity-norm bound on the largest natural frequency squared."""
    M, C, K, f, g = s.matrices()
    row = np.abs(K).sum(axis=1) / np.diag(M)
    return float(np.max(row))


print(line)
print("A. is the fast-time-scale bound sound?")
print(line)
ens = ensemble(seed=5, count=300, n_lo=2, n_hi=8)
ratios = []
for s in ens:
    t = true_omega_max_sq(s)
    b = fast_bound(s)
    ratios.append(t / b if b > 0 else float("nan"))
r = np.array(ratios)
print("  structures                : " + str(len(ratios)))
print("  max ratio true/bound      : " + format(float(r.max()), ".6f"))
print("  violations (ratio > 1)    : " + str(int((r > 1 + 1e-9).sum())))
print("  median tightness          : " + format(float(np.median(1.0 / np.maximum(r, 1e-12))), ".3f"))
print()
if int((r > 1 + 1e-9).sum()) == 0:
    print("  -> sound on every network.  The infinity norm dominates the spectral radius,")
    print("     and M^-1 K is the matrix whose eigenvalues are the squared natural")
    print("     frequencies.")

print()
print(line)
print("B. the second ensemble family")
print(line)
ALT = dict(n_lo=2, n_hi=7, extra_edges=2, value_dist="uniform")
alt = ensemble(seed=900, count=N, **ALT)
print("  topology   : random tree PLUS 2 extra edges, so the graphs have loops")
print("  values     : uniform on the same ranges instead of log-uniform")
print("  n range    : 2..7 instead of 2..8")
print("  median n   : " + format(float(np.median([s.n for s in alt])), ".1f"))


def cuts_of(ens_set, pct):
    n = np.array([s.n for s in ens_set], dtype=float)
    sag = np.array([s.static_deflection() for s in ens_set])
    slow = np.array([sum(s.ground_k.values()) / s.masses.sum() for s in ens_set])
    fast = np.array([fast_bound(s) for s in ens_set])
    m = int(np.percentile(n, pct))
    return {
        "C1 modal": n < m,
        "C2 statics": sag > np.percentile(sag, pct),
        "C3 slow": slow > np.percentile(slow, pct),
        "C4 fast": fast < np.percentile(fast, 100 - pct),
    }


print()
print(line)
print("C. FOUR certificates, sequential conditionals, on both families")
print(line)
for tag, ens_set, pct in (("original family, 50th pct",
                           ensemble(seed=105, count=N, n_lo=2, n_hi=8), 50),
                          ("NEW family, 50th pct", alt, 50),
                          ("NEW family, 30th pct",
                           ensemble(seed=900, count=N, **ALT), 30)):
    c = cuts_of(ens_set, pct)
    keys = list(c)
    remain = np.ones(N, dtype=bool)
    seq = []
    print()
    print("  " + tag)
    print("    " + "cut".rjust(12) + "marginal".rjust(10) + "given previous".rjust(17)
          + "remaining".rjust(12))
    for k in keys:
        before = remain.copy()
        remain = remain & ~c[k]
        cond = 1 - remain.sum() / max(before.sum(), 1)
        seq.append({"cut": k, "marginal": float(c[k].mean()), "conditional": float(cond),
                    "remaining": float(remain.mean())})
        print("    " + k.rjust(12) + format(c[k].mean(), ".4f").rjust(10)
              + format(cond, ".4f").rjust(17) + format(remain.mean(), ".4f").rjust(12))
    surv = float(remain.mean())
    kk = math.log(1e10) / math.log(1 / surv) if 0 < surv < 1 else float("inf")
    print("    round survival " + format(surv, ".4f") + "   rounds for 1e10 "
          + format(kk, ".1f") + "   certificates " + format(4 * kk, ".0f"))

out = pathlib.Path(__file__).resolve().parents[1] / "runs"
out.mkdir(exist_ok=True)
(out / "fourth_certificate.json").write_text(json.dumps({
    "fast_bound_max_ratio": float(r.max()),
    "fast_bound_violations": int((r > 1 + 1e-9).sum()),
}, indent=1), encoding="utf-8")
print()
print("wrote runs/fourth_certificate.json")
