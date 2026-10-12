"""Step 32 - a numerically sound waterbed integral.

Both previous attempts were broken
----------------------------------
The u = ln(w) substitution turns the integrand into  ln|T| * exp(-u).  As w -> 0,
ln|T| = O(w^2) is computed by subtracting 1 from |T|, which is catastrophic cancellation,
and it is then MULTIPLIED by exp(-u), which diverges.  A tail that is genuinely zero is
turned into a large spurious number by a tiny relative error amplified by a huge factor.

  trapezoid, u in [-16, 22]   -> dominated by the noise amplification
  scipy.quad, u in [-40, 40]  -> worse, returns values of order 100 with an
                                 IntegrationWarning, and gives the SAME value 52.266 for
                                 different structures, which is the signature of a
                                 quadrature failing rather than a quantity being measured

The fix is to integrate in w directly, which keeps the weight bounded, and to add the two
tails analytically.  Near zero the integrand tends to a finite constant c; at infinity
ln|T| ~ ln(A/w).
"""
import _bootstrap  # noqa: F401
import json
import pathlib

import numpy as np

from ecdr.structure import Structure, ensemble
from ecdr.l0 import PassiveSDOF

line = "=" * 88


def waterbed_stable(s: Structure, w_lo=1e-4, w_hi=1e9, n=60000):
    """W = integral ln|T|/w^2 dw, integrated in w with analytic tails."""
    w = np.logspace(np.log10(w_lo), np.log10(w_hi), n)
    T = np.abs(s.transmissibility(w))
    W = float(np.trapezoid(np.log(T) / w ** 2, w))
    # small-w tail:  integrand -> c  as w -> 0,  contribution ~ c * w_lo
    Tlo = float(np.abs(s.transmissibility(np.array([w_lo])))[0])
    c = np.log(Tlo) / w_lo ** 2
    W += c * w_lo
    # large-w tail:  |T| ~ A/w  so ln|T| ~ ln A - ln w
    Thi = float(np.abs(s.transmissibility(np.array([w_hi])))[0])
    A = Thi * w_hi
    W += (np.log(A) - np.log(w_hi) - 1.0) / w_hi
    return W


print(line)
print("A. control: the SDOF, where the contour argument and every earlier run agree on 0")
print(line)
wn, z, m1 = 99.03, 0.5426, 1.0
s1 = Structure(masses=np.array([m1]), springs={}, dampers={},
               ground_k={0: wn ** 2 * m1}, ground_c={0: 2 * z * wn * m1})
print("  SDOF  W = " + format(waterbed_stable(s1), ".6e"))

print()
print(line)
print("B. the structures the trapezoid flagged, recomputed in w")
print(line)
ens = ensemble(seed=5, count=200, n_lo=2, n_hi=8)
flagged = [76, 199, 33, 101, 47, 185, 90, 147, 134, 138]
print("  " + "index".rjust(7) + "n".rjust(4) + "old trap".rjust(18) + "in w".rjust(20)
      + "  verdict".rjust(16))
old = {76: 1.21109698e-02, 199: 1.10972437e-02, 33: 8.78876774e-03, 101: 7.31088761e-03,
       47: 6.68782150e-03, 185: 5.01511190e-03, 90: 4.35774568e-03, 147: 3.56851663e-03,
       134: 2.85358317e-03, 138: 2.11628406e-03}
rows = []
for i in flagged:
    v = waterbed_stable(ens[i])
    rows.append({"index": i, "n": ens[i].n, "old_trap": old[i], "in_w": v})
    print("  " + str(i).rjust(7) + str(ens[i].n).rjust(4) + format(old[i], ".6e").rjust(18)
          + format(v, ".6e").rjust(20) + "  " + ("ZERO" if abs(v) < 1e-6 else "non-zero").rjust(16))

print()
print(line)
print("C. the whole ensemble, in w")
print(line)
W = np.array([waterbed_stable(s) for s in ens])
print("  median abs W : " + format(float(np.median(np.abs(W))), ".3e"))
print("  max    abs W : " + format(float(np.abs(W).max()), ".3e"))
for thr in (1e-9, 1e-6, 1e-4, 1e-3, 1e-2):
    print("  |W| > " + format(thr, ".0e").rjust(8) + " : " + str(int((np.abs(W) > thr).sum())).rjust(4)
          + " of 200")

out = pathlib.Path(__file__).resolve().parents[1] / "runs"
out.mkdir(exist_ok=True)
(out / "waterbed_stable.json").write_text(json.dumps({
    "sdof": waterbed_stable(s1),
    "flagged": rows,
    "median_abs": float(np.median(np.abs(W))),
    "max_abs": float(np.abs(W).max()),
    "counts": {format(t, ".0e"): int((np.abs(W) > t).sum())
               for t in (1e-9, 1e-6, 1e-4, 1e-3, 1e-2)},
}, indent=1), encoding="utf-8")
print()
print("wrote runs/waterbed_stable.json")
