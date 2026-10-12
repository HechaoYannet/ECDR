"""Step 54 - simulates the L1 lagged sky-hook, which has never been simulated.

Why this matters more than another certificate
----------------------------------------------
ecdr/l1/models.py states, without derivation in the file and without any simulation check:

    T(s) = k (s + omega_a) / [ (m s^2 + k)(s + omega_a) + c_sky omega_a s ]

and
    actuator force per unit ground displacement = c_sky * (omega_a / sqrt(w^2 + omega_a^2)) * w * |T|

Every L1 conclusion rests on those two expressions - the actuator-bandwidth study, the
false-positive zone of Finding 008, the claim that the active mechanism escapes the
passive bound with a factor of 20 of margin.  Both were derived by hand and neither has
ever been checked against an integration of the underlying equations.

The physics they are supposed to represent, with unit payload mass:

    x'' = -k (x - x_g) + F            F is the force the actuator applies TO the mass
    F'  = omega_a ( -c_sky x' - F )   the commanded force -c_sky x' through a first-order lag

This integrates exactly that and compares.
"""
import _bootstrap  # noqa: F401
import json
import pathlib

import numpy as np

from ecdr.l1.models import LaggedSkyHook
from ecdr.l2 import state_space_amplitude

line = "=" * 92
print(line)
print("L1 LAGGED SKY-HOOK: hand-derived closed form vs time-domain integration")
print(line)

mech = LaggedSkyHook()
cases = [(60.0, 0.5, 60.0), (60.0, 0.5, 600.0), (120.0, 0.7, 1.0e4),
         (40.0, 1.2, 300.0)]

rows = []
for wn, z, wa in cases:
    k = wn ** 2
    c_sky = 2.0 * z * wn
    # state (x, v, F)
    A = np.array([[0.0, 1.0, 0.0],
                  [-k, 0.0, 1.0],
                  [0.0, -c_sky * wa, -wa]])
    B1 = np.array([0.0, k, 0.0])
    B2 = np.zeros(3)
    cx = np.array([1.0, 0.0, 0.0])
    cF = np.array([0.0, 0.0, 1.0])

    omegas = np.array([0.25 * wn, 1.0 * wn, 3.0 * wn])
    ref_T = np.abs(mech.transmissibility(omegas, (wn, z, wa)))
    ref_F = np.abs(mech.actuator_force_per_disp(omegas, (wn, z, wa)))
    got_T = state_space_amplitude(A, B1, B2, cx, omegas, periods=200,
                                  samples_per_period=1000)
    got_F = state_space_amplitude(A, B1, B2, cF, omegas, periods=200,
                                  samples_per_period=1000)

    print()
    print("  omega_n = " + format(wn, ".4g") + ",  zeta = " + format(z, ".3g")
          + ",  omega_a = " + format(wa, ".4g"))
    print("    " + "omega".rjust(12) + "|T| closed".rjust(16) + "|T| simulated".rjust(16)
          + "rel".rjust(10) + "|F| closed".rjust(16) + "|F| simulated".rjust(16) + "rel".rjust(10))
    for w, a, b, fa, fb in zip(omegas, ref_T, got_T, ref_F, got_F):
        rT = abs(a - b) / max(abs(a), 1e-12)
        rF = abs(fa - fb) / max(abs(fa), 1e-12)
        rows.append({"wn": wn, "z": z, "wa": wa, "omega": float(w),
                     "T_ref": float(a), "T_sim": float(b), "rel_T": float(rT),
                     "F_ref": float(fa), "F_sim": float(fb), "rel_F": float(rF)})
        print("    " + format(w, ".5g").rjust(12) + format(a, ".8e").rjust(16)
              + format(b, ".8e").rjust(16) + format(rT, ".2e").rjust(10)
              + format(fa, ".8e").rjust(16) + format(fb, ".8e").rjust(16)
              + format(rF, ".2e").rjust(10))

rT = np.array([r["rel_T"] for r in rows])
rF = np.array([r["rel_F"] for r in rows])
print()
print(line)
print("VERDICT")
print(line)
print("  comparisons              : " + str(len(rows)))
print("  |T|   median / worst rel : " + format(float(np.median(rT)), ".3e") + " / "
      + format(float(rT.max()), ".3e"))
print("  |F|   median / worst rel : " + format(float(np.median(rF)), ".3e") + " / "
      + format(float(rF.max()), ".3e"))
print()
if rT.max() < 1e-3 and rF.max() < 1e-3:
    print("  Both closed forms are CONFIRMED against a direct integration of the underlying")
    print("  equations.  The L1 conclusions rest on expressions that now have an independent")
    print("  numerical check.")
else:
    print("  MISMATCH.  The closed form and the integration disagree, so one of them does not")
    print("  represent the stated physics and every L1 conclusion is unsafe.")

out = pathlib.Path(__file__).resolve().parents[1] / "runs"
out.mkdir(exist_ok=True)
(out / "l1_crossvalidation.json").write_text(json.dumps({
    "rows": rows,
    "T_median_rel": float(np.median(rT)), "T_max_rel": float(rT.max()),
    "F_median_rel": float(np.median(rF)), "F_max_rel": float(rF.max()),
}, indent=1), encoding="utf-8")
print()
print("wrote runs/l1_crossvalidation.json")
