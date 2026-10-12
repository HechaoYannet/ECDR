"""Step 36 - the closed form, with coefficients from a well-conditioned fit and roots
from high precision, verified against the TRUE P.

Three corrections over step 35, each of which had made the check unable to fail:

  1. coefficients came from an exact solve of a 14-point Vandermonde, which amplifies the
     1e-16 error in the sample values without averaging it down.  Step 34's 60-point
     least-squares fit (SVD based) was better.  Use many points.
  2. the degree was fitted as 2n, but deg P <= 2n - 1.  Use 2n - 1.
  3. the "verification" evaluated the FITTED polynomial at its own roots, which polyroots
     guarantees to be zero.  That verified nothing.  Verify against P computed from the
     matrices instead.

The candidate formula is  W = pi * sum over RHP zeros of Re(1/z).
"""
import _bootstrap  # noqa: F401
import json
import pathlib

import mpmath as mp
import numpy as np

from ecdr.structure import Structure, ensemble, waterbed_numeric

mp.mp.dps = 60
line = "=" * 94


def sigma_of(s: Structure) -> float:
    M, C, K, f, g = s.matrices()
    return 1.0 / float(np.sqrt(np.max(np.abs(K)) / np.max(M)))


def true_P(s: Structure, points):
    """P evaluated from the matrices - the ground truth, independent of any fit."""
    M, C, K, f, g = s.matrices()
    out = np.empty(len(points))
    for i, si in enumerate(points):
        A = M * si ** 2 + C * si + K
        out[i] = np.linalg.det(A) * np.linalg.solve(A, f + g * si)[0]
    return out


def analyse(s: Structure):
    deg = 2 * s.n - 1
    sigma = sigma_of(s)
    m = 8 * deg + 20
    t = np.linspace(1.0, 8.0, m)
    vals = true_P(s, t / sigma)
    coef_t = np.polynomial.polynomial.polyfit(t, vals, deg)
    coef = [mp.mpf(float(coef_t[k])) * mp.mpf(sigma) ** k for k in range(deg + 1)]
    roots = mp.polyroots(coef, maxsteps=400, extraprec=800)
    scale = max(abs(c) for c in coef)
    # TRUE verification: evaluate P from the matrices at each candidate root
    cands = [complex(r) for r in roots if r.real > mp.mpf("1e-12")]
    if cands:
        pv = np.abs(true_P(s, np.array(cands)))
        worst = float(np.max(pv) / float(scale))
    else:
        worst = 0.0
    total = sum((1 / r).real for r in roots if r.real > mp.mpf("1e-12"))
    return float(mp.pi * total), worst, len(cands)


print(line)
print("A. the formula against the integral, roots verified against the true P")
print(line)
ens = ensemble(seed=5, count=200, n_lo=2, n_hi=8)
Wnum = np.array([waterbed_numeric(s) for s in ens])
Wpred = np.empty(200)
rootres = np.empty(200)
nrhp = np.empty(200, dtype=int)
for i, s in enumerate(ens):
    v, w, k = analyse(s)
    Wpred[i], rootres[i], nrhp[i] = v, w, k

print("  max |P(z)|/scale at candidate roots, over 200 networks : "
      + format(float(rootres.max()), ".3e"))
print("  (scale is the largest fitted coefficient; a genuine root makes this small)")
print()
print("  " + "index".rjust(7) + "n".rjust(4) + "RHPz".rjust(6) + "W numeric".rjust(18)
      + "pi*sum Re(1/z)".rjust(18) + "ratio".rjust(11) + "|P(z)|/scale".rjust(13))
for i in [76, 199, 33, 101, 47, 185, 90, 147, 134, 138]:
    r = Wpred[i] / Wnum[i] if abs(Wnum[i]) > 1e-300 else float("nan")
    print("  " + str(i).rjust(7) + str(ens[i].n).rjust(4) + str(nrhp[i]).rjust(6)
          + format(Wnum[i], ".8e").rjust(18) + format(Wpred[i], ".8e").rjust(18)
          + format(r, ".6f").rjust(11) + format(float(rootres[i]), ".1e").rjust(13))

good = rootres < 1e-6
print()
print("  candidate roots verified (|P(z)|/scale < 1e-6) : " + str(int(good.sum())) + " of 200")
comp = good & (np.abs(Wnum) > 1e-6)
rel = np.abs(Wpred[comp] - Wnum[comp]) / np.abs(Wnum[comp])
print("  comparable networks (verified and |W| > 1e-6)  : " + str(int(comp.sum())))
if comp.sum():
    print("  median relative difference : " + format(float(np.median(rel)), ".3e"))
    print("  max    relative difference : " + format(float(rel.max()), ".3e"))
    wi = int(np.where(comp)[0][int(np.argmax(rel))])
    print("  worst: index " + str(wi) + ", n = " + str(ens[wi].n)
          + ", ratio " + format(float(Wpred[wi] / Wnum[wi]), ".6f"))
    print()
    if float(np.median(rel)) < 1e-3:
        print("  VERDICT: CONFIRMED.  W = pi * sum over RHP zeros of Re(1/z).")
    else:
        print("  VERDICT: not confirmed at 1e-3.")

print()
print(line)
print("B. the vanishing prediction")
print(line)
z = nrhp == 0
print("  networks with no RHP zero : " + str(int(z.sum())))
if z.any():
    print("    max |W numeric|        : " + format(float(np.abs(Wnum[z]).max()), ".3e"))
    print("    max |pi sum Re(1/z)|   : " + format(float(np.abs(Wpred[z]).max()), ".3e"))

out = pathlib.Path(__file__).resolve().parents[1] / "runs"
out.mkdir(exist_ok=True)
(out / "waterbed_formula_final.json").write_text(json.dumps({
    "max_root_residual": float(rootres.max()),
    "verified": int(good.sum()), "compared": int(comp.sum()),
    "median_rel_diff": float(np.median(rel)) if comp.sum() else None,
    "max_rel_diff": float(rel.max()) if comp.sum() else None,
    "no_rhp_zero_count": int(z.sum()),
    "no_rhp_zero_max_W": float(np.abs(Wnum[z]).max()) if z.any() else None,
}, indent=1), encoding="utf-8")
print()
print("wrote runs/waterbed_formula_final.json")
