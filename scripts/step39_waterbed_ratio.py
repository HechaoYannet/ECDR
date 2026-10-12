"""Step 39 - the ratio distribution, with no residual filter that can hide failures.

The residual check overflows: at a root with |z| ~ 1e10, det(M s^2 + ...) with s^2 ~ 1e20
overflows float64, so |P(z)|/scale comes out as inf or 1e70 whether or not the root is
good.  It cannot be used as a filter.

The direct test is the ratio W_formula / W_numeric.  Report its distribution over every
network where W_numeric is above its own noise floor, and separately report how the ratio
depends on the polynomial degree, which is where the root finder is expected to degrade.
"""
import _bootstrap  # noqa: F401
import json
import pathlib

import mpmath as mp
import numpy as np

from ecdr.structure import Structure, ensemble, waterbed_numeric

mp.mp.dps = 60
line = "=" * 84


def P_at(s, points):
    M, C, K, f, g = s.matrices()
    out = np.empty(len(points), dtype=complex)
    for i, si in enumerate(points):
        A = M * si ** 2 + C * si + K
        out[i] = np.linalg.det(A) * np.linalg.solve(A, f + g * si)[0]
    return out


def predicted(s: Structure):
    deg = 2 * s.n - 1
    M, C, K, f, g = s.matrices()
    sigma = 1.0 / float(np.sqrt(np.max(np.abs(K)) / np.max(M)))
    m = 8 * deg + 20
    t = np.linspace(1.0, 8.0, m)
    vals = P_at(s, t / sigma).real
    ct = np.polynomial.polynomial.polyfit(t, vals, deg)
    asc = [float(ct[k]) * sigma ** k for k in range(deg + 1)]
    roots = mp.polyroots([mp.mpf(c) for c in reversed(asc)],
                         maxsteps=600, extraprec=1200)
    rhp = [r for r in roots if r.real > mp.mpf("1e-12")]
    return float(mp.pi * sum((1 / r).real for r in rhp)), len(rhp)


ens = ensemble(seed=5, count=200, n_lo=2, n_hi=8)
Wnum = np.array([waterbed_numeric(s) for s in ens])
Wp = np.empty(200)
nz = np.empty(200, dtype=int)
for i, s in enumerate(ens):
    Wp[i], nz[i] = predicted(s)

big = np.abs(Wnum) > 1e-6
ratio = np.where(big, Wp / np.where(big, Wnum, 1.0), np.nan)

print(line)
print("A. ratio W_formula / W_numeric, over every network with |W_numeric| > 1e-6")
print(line)
r = ratio[big]
good = np.abs(r - 1.0) < 1e-3
print("  networks compared          : " + str(int(big.sum())))
print("  ratio within 1e-3 of 1     : " + str(int(good.sum())) + " of " + str(int(big.sum())))
print("  median |ratio - 1|         : " + format(float(np.median(np.abs(r - 1))), ".3e"))
print()
print("  " + "index".rjust(7) + "n".rjust(4) + "deg".rjust(5) + "RHPz".rjust(6)
      + "W numeric".rjust(18) + "pi*sum Re(1/z)".rjust(18) + "ratio".rjust(12))
# r is indexed by POSITION within the selected subset, not by network index
for j, i in enumerate(np.where(big)[0]):
    print("  " + str(i).rjust(7) + str(ens[i].n).rjust(4) + str(2 * ens[i].n - 1).rjust(5)
          + str(nz[i]).rjust(6) + format(Wnum[i], ".8e").rjust(18)
          + format(Wp[i], ".8e").rjust(18) + format(float(r[j]), ".6f").rjust(12))

print()
print(line)
print("B. the ratio against polynomial degree - where the root finder degrades")
print(line)
print("  " + "n".rjust(4) + "degree".rjust(8) + "compared".rjust(10) + "within 1e-3".rjust(12)
      + "median |ratio-1|".rjust(18))
bydeg = []
for n in sorted(set(ens[i].n for i in np.where(big)[0])):
    sel = big & np.array([s.n == n for s in ens])
    rr = ratio[sel]
    g = int(np.sum(np.abs(rr - 1.0) < 1e-3))
    bydeg.append({"n": int(n), "degree": 2 * n - 1, "compared": int(sel.sum()),
                  "within": g, "median_err": float(np.median(np.abs(rr - 1)))})
    print("  " + str(n).rjust(4) + str(2 * n - 1).rjust(8) + str(int(sel.sum())).rjust(10)
          + str(g).rjust(12) + format(float(np.median(np.abs(rr - 1))), ".3e").rjust(18))

print()
print(line)
print("C. the vanishing prediction")
print(line)
z = nz == 0
print("  networks with no RHP zero : " + str(int(z.sum())))
if z.any():
    print("    max |W numeric|        : " + format(float(np.abs(Wnum[z]).max()), ".3e"))
    print("    max |pi sum Re(1/z)|   : " + format(float(np.abs(Wp[z]).max()), ".3e"))

out = pathlib.Path(__file__).resolve().parents[1] / "runs"
out.mkdir(exist_ok=True)
(out / "waterbed_ratio.json").write_text(json.dumps({
    "compared": int(big.sum()), "within_1e-3": int(good.sum()),
    "median_abs_err": float(np.median(np.abs(r - 1))),
    "by_degree": bydeg,
    "no_rhp_zero_count": int(z.sum()),
    "no_rhp_zero_max_W": float(np.abs(Wnum[z]).max()) if z.any() else None,
}, indent=1), encoding="utf-8")
print()
print("wrote runs/waterbed_ratio.json")
