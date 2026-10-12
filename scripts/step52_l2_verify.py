"""Step 52 - cross-validate L0/L1 against an independent numerical route (L2).

For a stable LTI system the steady-state amplitude of the payload under a unit sinusoidal
ground displacement IS the transmissibility magnitude.  L0 and L1 compute it from the
algebraic frequency-domain system; L2 integrates the ODE in Julia and measures it.  The two
routes share no formula, so agreement is evidence about the assembly and the algebra rather
than about the physics.

Reported for several structures and several frequencies, including frequencies below, near
and above the first resonance, since a sign or assembly error is most visible near resonance
and in the high-frequency decay.
"""
import _bootstrap  # noqa: F401
import json
import pathlib

import numpy as np

from ecdr.structure import ensemble

line = "=" * 90
print(line)
print("L2 CROSS-VALIDATION: frequency domain (L0/L1) against time domain (Julia)")
print(line)

try:
    from ecdr.l2 import available, transmissibility_time_domain
except Exception as exc:  # pragma: no cover
    print("  L2 unavailable: " + str(exc))
    raise SystemExit(0)

if not available():
    print("  juliacall not importable; L2 skipped")
    raise SystemExit(0)

ens = ensemble(seed=5, count=40, n_lo=2, n_hi=5)
picked = [ens[0], ens[1], ens[2], ens[7]]

rows = []
for idx, s in enumerate(picked):
    # choose frequencies spread around this structure's own first resonance
    M, C, K, f, g = s.matrices()
    ev = np.sort(np.linalg.eigvals(np.diag(1.0 / np.diag(M)) @ K).real)
    w1 = float(np.sqrt(max(ev[0], 1e-12)))
    omegas = np.array([0.3 * w1, 1.0 * w1, 4.0 * w1])
    ref = np.abs(s.transmissibility(omegas))
    got = transmissibility_time_domain(s, omegas, periods=80, samples_per_period=600)
    print()
    print("  structure " + str(idx) + ":  n = " + str(s.n)
          + ",  first resonance omega_1 = " + format(w1, ".4g"))
    print("    " + "omega".rjust(14) + "frequency domain".rjust(20) + "time domain".rjust(18)
          + "relative diff".rjust(16))
    for w, a, b in zip(omegas, ref, got):
        rel = abs(a - b) / max(abs(a), 1e-12)
        rows.append({"i": idx, "n": s.n, "omega": float(w), "freq": float(a),
                     "time": float(b), "rel": float(rel)})
        print("    " + format(w, ".6g").rjust(14) + format(a, ".10e").rjust(20)
              + format(b, ".10e").rjust(18) + format(rel, ".3e").rjust(16))

rel = np.array([r["rel"] for r in rows])
print()
print(line)
print("VERDICT")
print(line)
print("  comparisons            : " + str(len(rows)))
print("  median relative diff   : " + format(float(np.median(rel)), ".3e"))
print("  worst relative diff    : " + format(float(rel.max()), ".3e"))
print("  within 1e-3            : " + str(int((rel < 1e-3).sum())) + " of " + str(len(rel)))
print()
if rel.max() < 1e-2:
    print("  The two routes agree.  An error in the frequency-domain algebra, in the")
    print("  assembly of M, C, K, f, g, or in the sign of the ground coupling would have to")
    print("  appear in one route and not the other, so agreement is evidence about both.")
    print()
    print("  It is NOT evidence about the equations of motion themselves: both routes")
    print("  solve the same M x'' + C x' + K x = f x_g + g x_g'.  Modelling independence")
    print("  needs a different paradigm, which was the Modelica decision and is not")
    print("  available here.")
else:
    print("  The routes DISAGREE.  Investigate before using either for L2 conclusions.")

out = pathlib.Path(__file__).resolve().parents[1] / "runs"
out.mkdir(exist_ok=True)
(out / "l2_crossvalidation.json").write_text(json.dumps({
    "rows": rows,
    "median_rel": float(np.median(rel)), "max_rel": float(rel.max()),
}, indent=1), encoding="utf-8")
print()
print("wrote runs/l2_crossvalidation.json")
