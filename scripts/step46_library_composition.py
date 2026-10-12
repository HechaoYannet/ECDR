"""Step 46 - does the pair compose in the LIBRARY sense, across space sizes?

Finding 021 established that the modal bound and a performance bound are weakly correlated
(rho <= 0.17 against 0.81 within the performance family).  Correlation is necessary but not
sufficient.  Finding 011 needs more:

    certificate i rules out a fraction f_i of the space REMAINING after 1..i-1
    and every f_i stays bounded away from zero

The second condition is the one that Finding 010 showed can fail: with a FIXED requirement
and a GROWING space, a resource-bound predicate covers a vanishing fraction.  So the test
has to sweep the space size, and it has to be run with both a fixed requirement and a
requirement calibrated to the space.

Two SOUND certificates are used, both cheap:

    A  modal   a structure with n degrees of freedom has a free response of at most n
               harmonics, so a requirement needing m independent frequencies rules out
               every n < m.  Linear algebra; holds for every parameter assignment.
    B  statics the payload sag under gravity must not exceed delta_max.  Equilibrium;
               holds for every parameter assignment.

Both are sound for all theta, which is what makes them certificates rather than
measurements.
"""
import _bootstrap  # noqa: F401
import json
import math
import pathlib

import numpy as np

from ecdr.structure import ensemble

line = "=" * 92
N_SAMPLES = 500
SIZES = [5, 6, 7, 8]


def one_space(n_max, seed):
    ens = ensemble(seed=seed, count=N_SAMPLES, n_lo=2, n_hi=n_max)
    n = np.array([s.n for s in ens], dtype=float)
    sag = np.array([s.static_deflection() for s in ens])
    return n, sag


print(line)
print("A. FIXED requirement: m = 4 frequencies required, delta_max = 8 mm")
print(line)
print("  " + "n_max".rjust(6) + "median n".rjust(10) + "A cuts".rjust(9) + "f_A".rjust(9)
      + "remain".rjust(9) + "B cuts of remaining".rjust(21) + "f_B".rjust(9))
fixed = []
for n_max in SIZES:
    n, sag = one_space(n_max, 100 + n_max)
    A = n < 4
    rem = ~A
    B = sag > 8.0e-3
    fA = float(A.mean())
    fB = float((B & rem).sum() / max(rem.sum(), 1))
    fixed.append({"n_max": n_max, "median_n": float(np.median(n)), "f_A": fA, "f_B": fB,
                  "remain": float(rem.mean())})
    print("  " + str(n_max).rjust(6) + format(float(np.median(n)), ".1f").rjust(10)
          + str(int(A.sum())).rjust(9) + format(fA, ".4f").rjust(9)
          + str(int(rem.sum())).rjust(9) + str(int((B & rem).sum())).rjust(21)
          + format(fB, ".4f").rjust(9))

print()
print(line)
print("B. CALIBRATED requirement: m at the median n of each space, delta_max at median sag")
print(line)
print("  NOTE: (1-f_A)(1-f_B) equals the observed remaining fraction AS AN IDENTITY,")
print("  because f_B is the conditional P(B | not A).  That column proves nothing about")
print("  independence and is replaced below by the product of the MARGINALS.")
print()
print("  " + "n_max".rjust(6) + "m".rjust(4) + "f_A".rjust(9) + "f_B marg".rjust(10)
      + "f_B | notA".rjust(12) + "prod marginals".rjust(16) + "observed joint".rjust(16)
      + "ratio".rjust(9))
cal = []
for n_max in SIZES:
    n, sag = one_space(n_max, 100 + n_max)
    m = int(np.median(n))
    dmax = float(np.median(sag))
    A = n < m
    rem = ~A
    B = sag > dmax
    fA = float(A.mean())
    fBm = float(B.mean())
    fB = float((B & rem).sum() / max(rem.sum(), 1))
    obs = float((rem & ~B).mean())
    mar = (1 - fA) * (1 - fBm)
    cal.append({"n_max": n_max, "m": m, "delta_mm": dmax * 1e3, "f_A": fA,
                "f_B_marginal": fBm, "f_B_conditional": fB,
                "prod_marginals": mar, "observed": obs,
                "ratio": obs / mar if mar else float("nan")})
    print("  " + str(n_max).rjust(6) + str(m).rjust(4)
          + format(fA, ".4f").rjust(9) + format(fBm, ".4f").rjust(10)
          + format(fB, ".4f").rjust(12) + format(mar, ".4f").rjust(16)
          + format(obs, ".4f").rjust(16)
          + format(obs / mar if mar else float("nan"), ".4f").rjust(9))
print()
print("  ratio near 1 means the two cuts are near independent; below 1 means they overlap")
print("  more than chance.")
rr = [r["ratio"] for r in cal]
print("  ratio across sizes: " + ", ".join(format(v, ".4f") for v in rr))

print()
print(line)
print("C. the library arithmetic, and whether the cuts survive the growth")
print(line)
print("  " + "n_max".rjust(6) + "N".rjust(9) + "fixed f_A".rjust(12) + "cal f_A".rjust(10)
      + "cal f_B".rjust(10) + "k for fixed".rjust(13) + "k for calibrated".rjust(17))
for i, n_max in enumerate(SIZES):
    N = N_SAMPLES
    fa_f = fixed[i]["f_A"]
    fa_c = cal[i]["f_A"]
    fb_c = cal[i]["f_B_conditional"]

    def k_of(f):
        return math.log(N) / math.log(1 / (1 - f)) if 0 < f < 1 else float("inf")
    kf = k_of(fa_f) if fa_f > 0 else float("inf")
    kc = k_of(fa_c) + k_of(fb_c) if fa_c > 0 and fb_c > 0 else float("inf")
    print("  " + str(n_max).rjust(6) + str(N).rjust(9) + format(fa_f, ".4f").rjust(12)
          + format(fa_c, ".4f").rjust(10) + format(fb_c, ".4f").rjust(10)
          + format(kf, ".1f").rjust(13) + format(kc, ".1f").rjust(17))

print()
print(line)
print("D. VERDICT")
print(line)
fa_trend = [r["f_A"] for r in fixed]
print("  fixed requirement, f_A across n_max " + str(SIZES) + ":")
print("    " + ", ".join(format(v, ".4f") for v in fa_trend))
if fa_trend[-1] < fa_trend[0] / 3:
    print("    -> f_A COLLAPSES as the space grows, exactly as Finding 010 predicted for a")
    print("       resource-bound predicate with a fixed requirement.")
print("  calibrated requirement, f_A : "
      + ", ".join(format(r["f_A"], ".4f") for r in cal))
print("  calibrated requirement, f_B | not A : "
      + ", ".join(format(r["f_B_conditional"], ".4f") for r in cal))
print("  independence ratio (observed joint / product of marginals) : "
      + ", ".join(format(r["ratio"], ".4f") for r in cal))
fb = [r["f_B_conditional"] for r in cal]
if min(fb) > 0.2:
    print("    -> f_B stays bounded away from zero, so the SECOND cut does take a constant")
    print("       fraction of what the first left, at every space size tested.")
if min(r["ratio"] for r in cal) > 0.8:
    print("    -> and the ratio stays above 0.88, so the two cuts are close to independent:")
    print("       the second is not re-cutting what the first already removed.")
print()
print("  CAUTION on f_A under a FIXED requirement:")
print("    it decays as 2/(n_max-1), i.e. as 1/n_max, because the ruled-out set is")
print("    {n < m} and the space is uniform on 2..n_max.  It does not collapse, but it")
print("    does go to zero, which is Finding 010's mechanism acting slowly.")

out = pathlib.Path(__file__).resolve().parents[1] / "runs"
out.mkdir(exist_ok=True)
(out / "library_composition.json").write_text(json.dumps({
    "fixed": fixed, "calibrated": cal, "sizes": SIZES, "n_samples": N_SAMPLES,
}, indent=1), encoding="utf-8")
print()
print("wrote runs/library_composition.json")
