"""Step 31 - is my trapezoid wrong, or is the contour argument wrong?

Two claims are in conflict.

  contour argument   W = integral ln|T|/w^2 dw = 0 exactly, for any T that is analytic
                     and non-zero in the closed right half plane with T(0) = 1.
                     Sketch: close the imaginary axis in the RHP.  The arc at infinity
                     vanishes because ln T ~ -ln s; the indentation at 0 vanishes because
                     ln T = O(s^2) there, which follows from T'(0)/T(0) = 0 (proved in
                     Finding 016).  An indentation around an interior zero also vanishes,
                     by O(eps log eps).  No poles inside, so the contour integral is zero.

  numerics           W is non-zero and converged for about 22 of 200 random networks,
                     as large as 1.2e-2, stable to 1e-8 under a tripled grid.

One of them is wrong.  A trapezoid rule can be wrong in ways refinement does not fix -
a mis-specified variable, a wrong Jacobian, a silently truncated tail.  scipy.quad on the
SAME substitution is an independent check, so it settles which side is broken.
"""
import _bootstrap  # noqa: F401
import json
import pathlib

import numpy as np
from scipy.integrate import quad

from ecdr.structure import ensemble

line = "=" * 88
ens = ensemble(seed=5, count=200, n_lo=2, n_hi=8)


def trap(s, u_lo=-16.0, u_hi=22.0, n=200000):
    u = np.linspace(u_lo, u_hi, n)
    T = np.abs(s.transmissibility(np.exp(u)))
    return float(np.trapezoid(np.log(np.maximum(T, 1e-300)) * np.exp(-u), u))


def adaptive(s, u_lo=-40.0, u_hi=40.0):
    def f(u):
        T = float(np.abs(s.transmissibility(np.array([np.exp(u)]))[0]))
        if T <= 0:
            return 0.0
        return np.log(T) * np.exp(-u)
    val, err = quad(f, u_lo, u_hi, limit=800, epsabs=1e-13, epsrel=1e-11)
    return float(val), float(err)


W = np.array([trap(s) for s in ens])
order = np.argsort(-np.abs(W))

print(line)
print("A. the ten largest trapezoid values, checked with scipy.quad")
print(line)
print("  " + "index".rjust(7) + "n".rjust(4) + "trapezoid".rjust(20) + "quad".rjust(20)
      + "quad err est".rjust(14) + "difference".rjust(14))
rows = []
for i in order[:10]:
    a = adaptive(ens[i])
    rows.append({"index": int(i), "n": int(ens[i].n), "trap": float(W[i]),
                 "quad": a[0], "quad_err": a[1]})
    print("  " + str(i).rjust(7) + str(ens[i].n).rjust(4) + format(W[i], ".8e").rjust(20)
          + format(a[0], ".8e").rjust(20) + format(a[1], ".2e").rjust(14)
          + format(abs(W[i] - a[0]), ".2e").rjust(14))

print()
print(line)
print("B. and on the structures the trapezoid says are zero")
print(line)
mid = [i for i in range(200) if i not in set(order[:10])][:5]
print("  " + "index".rjust(7) + "n".rjust(4) + "trapezoid".rjust(20) + "quad".rjust(20))
for i in mid:
    a = adaptive(ens[i])
    print("  " + str(i).rjust(7) + str(ens[i].n).rjust(4) + format(W[i], ".8e").rjust(20)
          + format(a[0], ".8e").rjust(20))

print()
print(line)
print("C. VERDICT")
print(line)
diffs = np.array([abs(r["trap"] - r["quad"]) for r in rows])
print("  max |trapezoid - quad| over the ten largest : " + format(float(diffs.max()), ".3e"))
print("  largest trapezoid value                     : " + format(float(np.abs(W).max()), ".3e"))
if diffs.max() < 1e-6 * max(np.abs(W).max(), 1e-30):
    print("  -> the two integrators AGREE.  The trapezoid is not the problem; the")
    print("     contour argument must have a hole.")
else:
    print("  -> the two integrators DISAGREE by more than the value in question, so the")
    print("     trapezoid was the broken side and W may well be zero after all.")

out = pathlib.Path(__file__).resolve().parents[1] / "runs"
out.mkdir(exist_ok=True)
(out / "waterbed_quadcheck.json").write_text(json.dumps({
    "largest": rows, "max_abs_trap": float(np.abs(W).max()),
    "max_trap_quad_diff": float(diffs.max()),
}, indent=1), encoding="utf-8")
print()
print("wrote runs/waterbed_quadcheck.json")
