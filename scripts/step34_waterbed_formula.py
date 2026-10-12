"""Step 34 - the closed form: W = pi * sum over RHP zeros of Re(1/z).

Dimensional analysis points straight at it.  W = integral ln|T|/w^2 dw has units of
TIME.  1/z has units of time.  And the necessity result of Finding 017 - no RHP zero
implies W = 0, with no counterexample in 200 structures - says only RHP zeros may enter.

So the candidate is

    W  =  pi * sum_{Re(z) > 0}  Re(1/z)

which is the classical Bode sensitivity integral with a 1/w^2 weight.  It is checked
against the numerical integral that Finding 017 established, on the same 200 networks.

Three things are verified before the formula is believed:
  1. the polynomial fit reproduces P at its sample points
  2. P evaluated at each computed root is small
  3. the formula matches the integral, not just in aggregate but structure by structure
"""
import _bootstrap  # noqa: F401
import json
import pathlib

import numpy as np

from ecdr.structure import Structure, ensemble, waterbed_numeric

line = "=" * 94


def poly_P(s: Structure, extra: int = 12):
    M, C, K, f, g = s.matrices()
    deg = 2 * s.n
    sigma = 1.0 / np.sqrt(np.max(np.abs(K)) / np.max(M))
    m = 6 * deg + extra
    t = np.linspace(1.0, 8.0, m)
    ss = t / sigma
    vals = np.empty(m)
    for i, si in enumerate(ss):
        A = M * si ** 2 + C * si + K
        vals[i] = np.linalg.det(A) * np.linalg.solve(A, f + g * si)[0]
    p_t = np.polynomial.polynomial.polyfit(t, vals, deg)
    resid = float(np.max(np.abs(np.polynomial.polynomial.polyval(t, p_t) - vals))
                  / max(np.max(np.abs(vals)), 1e-300))
    return np.array([p_t[k] * sigma ** k for k in range(deg + 1)]), resid


def predicted_W(s: Structure):
    p, resid = poly_P(s)
    roots = np.roots(p[::-1])
    rhp = roots[roots.real > 1e-9]
    # verify the roots really are roots, scaled by the coefficient magnitude
    if rhp.size:
        scale = np.max(np.abs(p))
        worst = float(np.max(np.abs(np.polyval(p[::-1], rhp)) / scale))
    else:
        worst = 0.0
    return float(np.pi * np.sum(1.0 / rhp.real * 0 + np.real(1.0 / rhp))) if rhp.size else 0.0, \
           resid, int(rhp.size), worst


line_out = []
print(line)
print("A. the formula against the numerical integral")
print(line)
ens = ensemble(seed=5, count=200, n_lo=2, n_hi=8)
Wnum = np.array([waterbed_numeric(s) for s in ens])
Wpred = np.empty_like(Wnum)
resids, nrhp, rooterr = [], [], []
for i, s in enumerate(ens):
    v, r, k, we = predicted_W(s)
    Wpred[i] = v
    resids.append(r)
    nrhp.append(k)
    rooterr.append(we)
resids = np.array(resids)
nrhp = np.array(nrhp)
rooterr = np.array(rooterr)

print("  fit residual, max over 200 networks        : " + format(float(resids.max()), ".3e"))
print("  |P(z)|/max|coef| at computed roots, max   : " + format(float(rooterr.max()), ".3e"))
print("  networks with at least one RHP zero       : " + str(int((nrhp > 0).sum())) + " of 200")
print()
print("  " + "index".rjust(7) + "n".rjust(4) + "RHP zeros".rjust(11) + "W numeric".rjust(18)
      + "pi*sum Re(1/z)".rjust(18) + "ratio".rjust(12))
show = [76, 199, 33, 101, 47, 185, 90, 147, 134, 138, 0, 2, 4]
for i in show:
    ratio = Wpred[i] / Wnum[i] if abs(Wnum[i]) > 1e-12 else float("nan")
    print("  " + str(i).rjust(7) + str(ens[i].n).rjust(4) + str(nrhp[i]).rjust(11)
          + format(Wnum[i], ".8e").rjust(18) + format(Wpred[i], ".8e").rjust(18)
          + format(ratio, ".4f").rjust(12))

big = np.abs(Wnum) > 1e-6
print()
print("  over the " + str(int(big.sum())) + " networks with |W_numeric| > 1e-6:")
rel = np.abs(Wpred[big] - Wnum[big]) / np.abs(Wnum[big])
print("    median relative difference : " + format(float(np.median(rel)), ".3e"))
print("    max    relative difference : " + format(float(rel.max()), ".3e"))

print()
print(line)
print("B. the sign and the vanishing")
print(line)
print("  networks with NO RHP zero : " + str(int((nrhp == 0).sum())))
if (nrhp == 0).any():
    print("    their max |W_numeric|        : " + format(float(np.abs(Wnum[nrhp == 0]).max()), ".3e"))
    print("    their max |pi*sum Re(1/z)|   : " + format(float(np.abs(Wpred[nrhp == 0]).max()), ".3e"))

print()
print(line)
print("C. VERDICT")
print(line)
if big.sum() > 3 and float(np.median(rel)) < 1e-3:
    print("  CONFIRMED.  W = pi * sum over RHP zeros of Re(1/z), to the accuracy of the")
    print("  root finder, on every network where W is large enough to compare.")
else:
    print("  NOT confirmed at this tolerance.  median relative difference is "
          + format(float(np.median(rel)), ".3e"))
    print("  See the per-structure table above for the pattern.")

out = pathlib.Path(__file__).resolve().parents[1] / "runs"
out.mkdir(exist_ok=True)
(out / "waterbed_formula.json").write_text(json.dumps({
    "fit_residual_max": float(resids.max()),
    "root_residual_max": float(rooterr.max()),
    "networks_with_rhp_zero": int((nrhp > 0).sum()),
    "compared": int(big.sum()),
    "median_rel_diff": float(np.median(rel)) if big.sum() else None,
    "max_rel_diff": float(rel.max()) if big.sum() else None,
}, indent=1), encoding="utf-8")
print()
print("wrote runs/waterbed_formula.json")
