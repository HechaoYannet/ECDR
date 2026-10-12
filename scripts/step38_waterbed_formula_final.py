"""Step 38 - the closed form, with mpmath's coefficient order finally right.

mpmath's polyroots and polyval take coefficients in DESCENDING order, exactly like
numpy.  Steps 35, 36 and 37 all passed ascending lists, which made the root finder solve
the reversed polynomial and made the "verification" check that same reversed polynomial at
those same wrong roots - self-consistent, and meaningless.

The evidence that this was the bug, from the single-network diagnostic:

    numpy  roots : 2 in RHP, |P(z)|/scale = 2.7e-07, pi*sum Re(1/z) = 1.21109588e-02
    mpmath roots : 2 in RHP, |P(z)|/scale = 1.0e+00, pi*sum Re(1/z) = 9.37593948e+01
    numerical waterbed integral W                                  = 1.2110968083e-02

numpy agreed to seven figures and mpmath did not, on the same coefficients.

Candidate formula:  W = pi * sum over right-half-plane zeros of Re(1/z)
"""
import _bootstrap  # noqa: F401
import json
import pathlib

import mpmath as mp
import numpy as np

from ecdr.structure import Structure, ensemble, waterbed_numeric

mp.mp.dps = 60
line = "=" * 94


def P_at(s: Structure, points):
    """P at COMPLEX points from the matrices - the ground truth, independent of any fit."""
    M, C, K, f, g = s.matrices()
    out = np.empty(len(points), dtype=complex)
    for i, si in enumerate(points):
        A = M * si ** 2 + C * si + K
        out[i] = np.linalg.det(A) * np.linalg.solve(A, f + g * si)[0]
    return out


def analyse(s: Structure):
    deg = 2 * s.n - 1                      # deg P <= 2n - 1, never 2n
    M, C, K, f, g = s.matrices()
    sigma = 1.0 / float(np.sqrt(np.max(np.abs(K)) / np.max(M)))
    m = 8 * deg + 20
    t = np.linspace(1.0, 8.0, m)
    vals = P_at(s, t / sigma).real
    coef_t = np.polynomial.polynomial.polyfit(t, vals, deg)
    coef_asc = [float(coef_t[k]) * sigma ** k for k in range(deg + 1)]
    scale = max(abs(c) for c in coef_asc)
    # DESCENDING for mpmath, as for numpy
    roots = mp.polyroots([mp.mpf(c) for c in reversed(coef_asc)],
                         maxsteps=600, extraprec=1200)
    rhp = [r for r in roots if r.real > mp.mpf("1e-12")]
    if rhp:
        pv = np.abs(P_at(s, np.array([complex(r) for r in rhp]))) / scale
        worst = float(np.max(pv))
    else:
        worst = 0.0
    total = float(mp.pi * sum((1 / r).real for r in rhp))
    return total, worst, len(rhp)


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

print("  max |P(z)|/scale at the RHP roots, over 200 networks : "
      + format(float(rootres.max()), ".3e"))
print()
print("  " + "index".rjust(7) + "n".rjust(4) + "RHPz".rjust(6) + "W numeric".rjust(18)
      + "pi*sum Re(1/z)".rjust(18) + "ratio".rjust(11) + "|P(z)|/scale".rjust(12))
for i in [76, 199, 33, 101, 47, 185, 90, 147, 134, 138]:
    r = Wpred[i] / Wnum[i] if abs(Wnum[i]) > 1e-300 else float("nan")
    print("  " + str(i).rjust(7) + str(ens[i].n).rjust(4) + str(nrhp[i]).rjust(6)
          + format(Wnum[i], ".8e").rjust(18) + format(Wpred[i], ".8e").rjust(18)
          + format(r, ".6f").rjust(11) + format(float(rootres[i]), ".1e").rjust(12))

comp = (rootres < 1e-4) & (np.abs(Wnum) > 1e-6)
print()
print("  roots that verify against the true P (|P|/scale < 1e-4) : "
      + str(int((rootres < 1e-4).sum())) + " of 200")
print("  comparable networks (verified AND |W| > 1e-6)           : " + str(int(comp.sum())))
rel = np.array([])
if comp.sum():
    rel = np.abs(Wpred[comp] - Wnum[comp]) / np.abs(Wnum[comp])
    print("  median relative difference : " + format(float(np.median(rel)), ".3e"))
    print("  max    relative difference : " + format(float(rel.max()), ".3e"))
    print("  fraction agreeing to 1e-3  : " + format(float(np.mean(rel < 1e-3)), ".4f"))
    print("  fraction agreeing to 1e-6  : " + format(float(np.mean(rel < 1e-6)), ".4f"))

print()
print(line)
print("B. the vanishing prediction")
print(line)
z = nrhp == 0
print("  networks with no RHP zero : " + str(int(z.sum())))
if z.any():
    print("    max |W numeric|        : " + format(float(np.abs(Wnum[z]).max()), ".3e"))
    print("    max |pi sum Re(1/z)|   : " + format(float(np.abs(Wpred[z]).max()), ".3e"))

print()
print(line)
print("C. VERDICT")
print(line)
if comp.sum() >= 10 and float(np.median(rel)) < 1e-4:
    print("  CONFIRMED:  W = pi * sum over right-half-plane zeros of Re(1/z).")
else:
    print("  median relative difference " + (format(float(np.median(rel)), ".3e")
                                             if comp.sum() else "n/a"))

out = pathlib.Path(__file__).resolve().parents[1] / "runs"
out.mkdir(exist_ok=True)
(out / "waterbed_formula_final.json").write_text(json.dumps({
    "max_root_residual": float(rootres.max()),
    "verified": int((rootres < 1e-4).sum()), "compared": int(comp.sum()),
    "median_rel_diff": float(np.median(rel)) if comp.sum() else None,
    "max_rel_diff": float(rel.max()) if comp.sum() else None,
    "frac_within_1e-3": float(np.mean(rel < 1e-3)) if comp.sum() else None,
    "no_rhp_zero_count": int(z.sum()),
    "no_rhp_zero_max_W": float(np.abs(Wnum[z]).max()) if z.any() else None,
}, indent=1), encoding="utf-8")
print()
print("wrote runs/waterbed_formula_final.json")
