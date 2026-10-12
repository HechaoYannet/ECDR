"""Step 35 - the same formula, with the root finding done properly.

Step 34 found the formula matching the integral to 1.0000 for degree 8 and 12
polynomials, and failing by factors of 17 to 33 for the higher degrees.  The tell was
|P(z)|/max|coef| = 2.1e+93 at the computed roots: numpy's companion-matrix eigenvalues
are the wrong tool for a degree-16 polynomial whose coefficients span many orders of
magnitude.

So the coefficients are fitted in HIGH PRECISION and the roots found with mpmath.  The
roots are then verified by evaluating P at them, again in high precision, and any network
whose roots do not check out is excluded rather than silently contributing a wrong number.

Two independent things must hold for the formula to be accepted:
  * the roots must actually be roots       (|P(z)| small relative to the coefficient scale)
  * pi * sum Re(1/z) must equal the integral
"""
import _bootstrap  # noqa: F401
import json
import pathlib

import mpmath as mp
import numpy as np

from ecdr.structure import Structure, ensemble, waterbed_numeric

mp.mp.dps = 60
line = "=" * 92


def sample_P(s: Structure, points):
    """P evaluated at the given complex points, in float64 - this part is well conditioned."""
    M, C, K, f, g = s.matrices()
    out = np.empty(len(points))
    for i, si in enumerate(points):
        A = M * si ** 2 + C * si + K
        out[i] = np.linalg.det(A) * np.linalg.solve(A, f + g * si)[0]
    return out


def coefficients_hp(s: Structure):
    """Monic-ish coefficients of P by a high-precision solve of the Vandermonde system."""
    # deg P <= 2n - 1, NOT 2n.  adj(A) has entries of degree at most 2n-2 and the
    # (f + g s) factor adds one.  Fitting degree 2n invents a leading coefficient that
    # is pure noise, and polyroots then returns one spurious root built from it.
    deg = 2 * s.n - 1
    sigma = 1.0 / float(np.sqrt(np.max(np.abs(s.matrices()[2])) / np.max(s.masses)))
    count = deg + 6
    t = np.linspace(1.0, 8.0, count)
    vals = sample_P(s, t / sigma)
    A = mp.matrix(count, deg + 1)
    for r in range(count):
        tr = mp.mpf(float(t[r]))
        for c in range(deg + 1):
            A[r, c] = tr ** c
    b = mp.matrix([mp.mpf(float(v)) for v in vals])
    coef_t = mp.lu_solve(A, b)
    return [coef_t[k] * mp.mpf(sigma) ** k for k in range(deg + 1)]


def predicted(s: Structure):
    coef = coefficients_hp(s)
    deg = len(coef) - 1
    roots = mp.polyroots(coef, maxsteps=400, extraprec=800)
    scale = max(abs(c) for c in coef)
    rhp = [r for r in roots if r.real > mp.mpf("1e-12")]
    # NOTE: mpmath's polyval and polyroots both take ASCENDING coefficients.  Passing
    # coef[::-1] here made the check evaluate the reversed polynomial and report a
    # residual of exactly 1.0, which looked like a catastrophic root failure and was
    # actually a reversed argument list.
    worst = max((abs(mp.polyval(coef, r)) / scale for r in rhp), default=mp.mpf(0))
    total = sum((1 / r).real for r in rhp)
    return float(mp.pi * total), float(worst), len(rhp)


print(line)
print("A. high-precision roots, verified before use")
print(line)
ens = ensemble(seed=5, count=200, n_lo=2, n_hi=8)
Wnum = np.array([waterbed_numeric(s) for s in ens])
Wpred = np.empty(200)
rootres = np.empty(200)
nrhp = np.empty(200, dtype=int)
for i, s in enumerate(ens):
    v, w, k = predicted(s)
    Wpred[i], rootres[i], nrhp[i] = v, w, k
print("  max |P(z)|/scale at computed roots : " + format(float(rootres.max()), ".3e"))
print("  networks with a verified RHP zero  : " + str(int((rootres < 1e-30).sum())) + " of 200")

ok = (rootres < 1e-30) & (np.abs(Wnum) > 1e-6)
print()
print("  " + "index".rjust(7) + "n".rjust(4) + "RHPz".rjust(6) + "W numeric".rjust(18)
      + "pi*sum Re(1/z)".rjust(18) + "ratio".rjust(11) + "|P(z)|/scale".rjust(13))
for i in [76, 199, 33, 101, 47, 185, 90, 147, 134, 138]:
    r = Wpred[i] / Wnum[i] if abs(Wnum[i]) > 1e-300 else float("nan")
    print("  " + str(i).rjust(7) + str(ens[i].n).rjust(4) + str(nrhp[i]).rjust(6)
          + format(Wnum[i], ".8e").rjust(18) + format(Wpred[i], ".8e").rjust(18)
          + format(r, ".6f").rjust(11) + format(float(rootres[i]), ".1e").rjust(13))

print()
print(line)
print("B. the formula against the integral, over every comparable network")
print(line)
rel = np.abs(Wpred[ok] - Wnum[ok]) / np.abs(Wnum[ok])
print("  networks compared (roots verified, |W| > 1e-6) : " + str(int(ok.sum())))
if ok.sum():
    print("  median relative difference : " + format(float(np.median(rel)), ".3e"))
    print("  max    relative difference : " + format(float(rel.max()), ".3e"))
    worst_i = int(np.argmax(np.where(ok, rel, -1)))
    print("  worst case index " + str(worst_i) + ", n = " + str(ens[worst_i].n)
          + ", ratio " + format(float(Wpred[worst_i] / Wnum[worst_i]), ".6f"))

print()
print(line)
print("C. the vanishing prediction")
print(line)
z = nrhp == 0
print("  networks with no RHP zero : " + str(int(z.sum())))
print("    max |W numeric|          : " + format(float(np.abs(Wnum[z]).max()), ".3e"))
print("    max |pi sum Re(1/z)|     : " + format(float(np.abs(Wpred[z]).max()), ".3e"))

out = pathlib.Path(__file__).resolve().parents[1] / "runs"
out.mkdir(exist_ok=True)
(out / "waterbed_formula_hp.json").write_text(json.dumps({
    "max_root_residual": float(rootres.max()),
    "verified": int((rootres < 1e-30).sum()),
    "compared": int(ok.sum()),
    "median_rel_diff": float(np.median(rel)) if ok.sum() else None,
    "max_rel_diff": float(rel.max()) if ok.sum() else None,
    "no_rhp_zero_count": int(z.sum()),
    "no_rhp_zero_max_W": float(np.abs(Wnum[z]).max()) if z.any() else None,
}, indent=1), encoding="utf-8")
print()
print("wrote runs/waterbed_formula_hp.json")
