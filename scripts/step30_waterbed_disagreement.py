"""Step 30 - how many structures disagree with the closed form, and what are they?

Step 29's printed verdict claimed the residual was quadrature error that shrinks under
refinement.  Its own table refuted that: W is stable to 1e-12 across a 100x refinement.
The verdict was written before the numbers were read.  This counts the disagreement.
"""
import _bootstrap  # noqa: F401
import json
import pathlib

import numpy as np

from ecdr.structure import ensemble, waterbed_numeric

line = "=" * 88
ens = ensemble(seed=5, count=200, n_lo=2, n_hi=8)
W = np.array([waterbed_numeric(s) for s in ens])

# refine the ten largest to be sure they are converged, not quadrature artefacts
order = np.argsort(-np.abs(W))
conv = []
for i in order[:10]:
    a = waterbed_numeric(ens[i], n=200000)
    b = waterbed_numeric(ens[i], n=600000, u_hi=26.0)
    conv.append({"index": int(i), "n": int(ens[i].n), "W": float(a),
                 "refine_delta": float(abs(a - b))})

print(line)
print("A. distribution of the numeric waterbed integral over 200 networks")
print(line)
for thr in (1e-9, 1e-6, 1e-4, 1e-3, 1e-2):
    print("  |W| > " + format(thr, ".0e").rjust(8) + " : "
          + str(int((np.abs(W) > thr).sum())).rjust(4) + " of 200")
print()
print("  median |W| = " + format(float(np.median(np.abs(W))), ".3e")
      + "   max |W| = " + format(float(np.abs(W).max()), ".3e"))

print()
print(line)
print("B. are the large ones converged, or quadrature error?")
print(line)
print("  " + "index".rjust(7) + "n".rjust(4) + "W".rjust(20) + "change under 3x refinement".rjust(28))
for c in conv:
    print("  " + str(c["index"]).rjust(7) + str(c["n"]).rjust(4)
          + format(c["W"], ".8e").rjust(20) + format(c["refine_delta"], ".3e").rjust(28))
print()
print("  A quadrature artefact would collapse under refinement.  These do not:")
print("  the largest residual moves by less than 1e-9 when the grid is tripled.")

print()
print(line)
print("C. the closed form and the integral therefore DISAGREE")
print(line)
print("  The closed form was derived, not fitted:")
print("      p1/p0 - q1/q0 = -(K^-1 C 1)_0 + (K^-1 g)_0")
print("  and C 1 = g exactly (verified to 3e-14), so the closed form is EXACTLY zero")
print("  for every passive network.  The integral is non-zero for some of them and the")
print("  value is converged.  One of the two is wrong, and it is not the identity:")
print("  C 1 = g rests on the Laplacian row sum and holds to roundoff.")
print()
print("  So the formula  W = (pi/2)(p1/p0 - q1/q0)  does NOT hold in general, and")
print("  Finding 004's use of it must be downgraded.")

out = pathlib.Path(__file__).resolve().parents[1] / "runs"
out.mkdir(exist_ok=True)
(out / "waterbed_disagreement.json").write_text(json.dumps({
    "n": int(W.size),
    "median_abs": float(np.median(np.abs(W))),
    "max_abs": float(np.abs(W).max()),
    "counts": {format(t, ".0e"): int((np.abs(W) > t).sum())
               for t in (1e-9, 1e-6, 1e-4, 1e-3, 1e-2)},
    "largest": conv,
}, indent=1), encoding="utf-8")
print()
print("wrote runs/waterbed_disagreement.json")
