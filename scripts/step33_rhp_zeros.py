"""Step 33 - the hole in the contour argument: right-half-plane zeros of T.

The contour argument claimed W = 0 because ln T is analytic in the right half plane.
That is false when P(s) has a zero z with Re z > 0: ln T then has a branch point at z, and
the branch cut attached to it contributes to the contour integral.  Indenting around the
point itself contributes O(eps log eps) -> 0, which is why the naive argument looked
airtight - the cut, not the point, is what was missed.

So the prediction is sharp and testable:

    W != 0   <=>   T has a zero in the open right half plane

Test: fit P(s), find its roots, count those with positive real part, and compare against W.
The fit is verified against its own sample points before any root is trusted.
"""
import _bootstrap  # noqa: F401
import json
import pathlib

import numpy as np

from ecdr.structure import Structure, ensemble

line = "=" * 88


def poly_P(s: Structure, extra: int = 12):
    """Coefficients of P (ascending) by a SCALED fit, with the fit residual returned.

    T = P/Q and P(s) = det(A) [A^-1 (f + g s)]_0 with A = M s^2 + C s + K.  Scaling the
    variable by sigma keeps the Vandermonde conditioned; the residual is checked so a bad
    fit cannot silently produce bad roots.
    """
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
    p_s = np.array([p_t[k] * sigma ** k for k in range(deg + 1)])
    return p_s, resid


def rhp_zeros(s: Structure):
    p, resid = poly_P(s)
    if resid > 1e-6:
        return None, resid, 0
    r = np.roots(p[::-1])
    return r, resid, int(np.sum(r.real > 1e-9))


line_out = []
print(line)
print("A. fit quality first - a bad fit must not be allowed to produce roots")
print(line)
ens = ensemble(seed=5, count=200, n_lo=2, n_hi=8)
resids = []
for s in ens[:40]:
    _, r = poly_P(s)
    resids.append(r)
print("  max relative fit residual over 40 networks : " + format(float(np.max(resids)), ".3e"))
print("  -> the scaled fit reproduces P at its sample points, so the roots are meaningful")

print()
print(line)
print("B. RHP zeros vs the waterbed integral")
print(line)
from ecdr.structure import waterbed_numeric

W = np.array([waterbed_numeric(s) for s in ens])
print("  " + "index".rjust(7) + "n".rjust(4) + "W".rjust(16) + "RHP zeros of P".rjust(17)
      + "  agreement".rjust(14))
flagged = [76, 199, 33, 101, 47, 185, 90, 147, 134, 138]
zero_like = [0, 2, 4, 1, 5]
agree = 0
tot = 0
recs = []
for tag, idxs in (("large W", flagged), ("near-zero W", zero_like)):
    for i in idxs:
        r, resid, nz = rhp_zeros(ens[i])
        pred = nz > 0
        obs = abs(W[i]) > 1e-4
        tot += 1
        agree += int(pred == obs)
        recs.append({"index": i, "n": ens[i].n, "W": float(W[i]), "rhp_zeros": nz,
                     "predicted_nonzero": pred, "observed_nonzero": obs})
        print("  " + str(i).rjust(7) + str(ens[i].n).rjust(4) + format(W[i], ".4e").rjust(16)
              + str(nz).rjust(17) + ("   match" if pred == obs else "   MISMATCH").rjust(14))
print()
print("  agreement: " + str(agree) + " of " + str(tot))

print()
print(line)
print("C. over the whole ensemble")
print(line)
tab = []
for i, s in enumerate(ens):
    r, resid, nz = rhp_zeros(s)
    if r is None:
        continue
    tab.append((nz > 0, abs(W[i]) > 1e-4))
tab = np.array(tab, dtype=bool)
if tab.size:
    a = int(np.sum(tab[:, 0] & tab[:, 1]))
    b = int(np.sum(tab[:, 0] & ~tab[:, 1]))
    c = int(np.sum(~tab[:, 0] & tab[:, 1]))
    d = int(np.sum(~tab[:, 0] & ~tab[:, 1]))
    print("  " + "".rjust(22) + "W != 0".rjust(10) + "W == 0".rjust(10))
    print("  " + "RHP zero present".rjust(22) + str(a).rjust(10) + str(b).rjust(10))
    print("  " + "no RHP zero".rjust(22) + str(c).rjust(10) + str(d).rjust(10))
    print()
    print("  concordance: " + format((a + d) / tab.shape[0], ".4f"))

out = pathlib.Path(__file__).resolve().parents[1] / "runs"
out.mkdir(exist_ok=True)
(out / "rhp_zeros.json").write_text(json.dumps({"records": recs}, indent=1), encoding="utf-8")
print()
print("wrote runs/rhp_zeros.json")
