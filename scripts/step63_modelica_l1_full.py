"""Step 63 - the whole L1 cross-validation through Modelica.

Finding 027 confirmed the L1 closed forms against a time-domain integration of the SAME
equations of motion.  That checks the algebra, the sign convention and the force law, but not
the equations themselves - both routes used the equations written in ecdr/l1/models.py.

This runs the same twelve comparisons against a model BUILT FROM MSL COMPONENTS, which
contains no equations of motion at all.  If they agree, the L1 expressions are confirmed
against equations this project did not write.

It also repeats the passive-network ensemble of Finding 031 through linearization, so the
structures that needed 1080 excitation periods in the time domain are now exact.
"""
import _bootstrap  # noqa: F401
import json
import pathlib

import numpy as np

from ecdr.l1.models import LaggedSkyHook
from ecdr.l2.modelica.emit import emit_model, emit_skyhook_model
from ecdr.l2.modelica.linearize import linearize, tf_mag
from ecdr.structure import ensemble

line = "=" * 104
OUT = pathlib.Path(__file__).resolve().parents[1] / "runs"

# ---------------------------------------------------------------- part A: the L1 mechanisms
print(line)
print("A. LAGED SKY-HOOK: L1 closed form vs a model with no equations of motion")
print(line)
mech = LaggedSkyHook()
ME = [(60.0, 0.5, 60.0), (60.0, 0.5, 600.0), (120.0, 0.7, 1.0e4), (40.0, 1.2, 300.0)]
rows = []
print("  " + "omega_n".rjust(9) + "zeta".rjust(7) + "omega_a".rjust(10)
      + "omega".rjust(10) + "|T| L1".rjust(17) + "|T| Modelica".rjust(17) + "|T| rel".rjust(10)
      + "|F| rel".rjust(10))
for ci, (wn, z, wa) in enumerate(ME):
    M = linearize(emit_skyhook_model(wn, z, wa, 1.0, name="Sky" + str(ci)),
                  name="Sky" + str(ci))
    if not M["ok"]:
        print("  case " + str(ci) + " FAILED: " + M["log"][-300:])
        continue
    for w in (0.25 * wn, 1.0 * wn, 3.0 * wn):
        refT = float(np.abs(mech.transmissibility(np.array([w]), (wn, z, wa)))[0])
        refF = float(np.abs(mech.actuator_force_per_disp(np.array([w]), (wn, z, wa)))[0])
        A, B, C, D = M["A"], M["B"], M["C"], M["D"]
        r = C @ np.linalg.solve(1j * w * np.eye(A.shape[0]) - A, B) + D
        gotT, gotF = float(abs(r[0, 0])), float(abs(r[1, 0]))
        relT = abs(gotT - refT) / refT
        relF = abs(gotF - refF) / refF
        rows.append({"wn": wn, "z": z, "wa": wa, "omega": float(w),
                     "T_L1": refT, "T_mod": gotT, "rel_T": relT,
                     "F_L1": refF, "F_mod": gotF, "rel_F": relF})
        print("  " + format(wn, ".4g").rjust(9) + format(z, ".3g").rjust(7)
              + format(wa, ".4g").rjust(10) + format(w, ".5g").rjust(10)
              + format(refT, ".9e").rjust(17) + format(gotT, ".9e").rjust(17)
              + format(relT, ".2e").rjust(10) + format(relF, ".2e").rjust(10))

# ------------------------------------------------------- part B: the passive networks too
print()
print(line)
print("B. PASSIVE NETWORKS through linearization (the ones Finding 031 needed 1080 periods for)")
print(line)
ens = ensemble(seed=5, count=40, n_lo=2, n_hi=6)
net_rows = []
for idx in (0, 1, 2, 3):
    s = ens[idx]
    Mx, Cx, Kx, fx, gx = s.matrices()
    ev = np.sort(np.linalg.eigvals(np.diag(1.0 / np.diag(Mx)) @ Kx).real)
    w1 = float(np.sqrt(max(ev[0], 1e-12)))
    Lm = linearize(emit_model(s, 1.0, name="Net" + str(idx)), name="Net" + str(idx))
    if not Lm["ok"]:
        print("  structure " + str(idx) + " FAILED: " + Lm["log"][-300:])
        continue
    for w in (0.6 * w1, 2.5 * w1):
        ref = float(np.abs(s.transmissibility(np.array([w])))[0])
        got = float(tf_mag(Lm, np.array([w]))[0])
        rel = abs(got - ref) / ref
        net_rows.append({"i": idx, "omega": float(w), "L0": ref, "modelica": got,
                         "rel": float(rel)})
        print("  structure " + str(idx) + "  n=" + str(s.n)
              + "  ground=" + str(len(s.ground_k))
              + "  omega=" + format(w, ".5g")
              + "   L0 " + format(ref, ".9e")
              + "   Modelica " + format(got, ".9e")
              + "   rel " + format(rel, ".2e"))

print()
print(line)
print("VERDICT")
print(line)
if rows:
    rT = np.array([r["rel_T"] for r in rows])
    rF = np.array([r["rel_F"] for r in rows])
    print("  L1 comparisons        : " + str(len(rows)))
    print("  |T| median / worst rel: " + format(float(np.median(rT)), ".3e") + " / "
          + format(float(rT.max()), ".3e"))
    print("  |F| median / worst rel: " + format(float(np.median(rF)), ".3e") + " / "
          + format(float(rF.max()), ".3e"))
if net_rows:
    rn = np.array([r["rel"] for r in net_rows])
    print("  network comparisons   : " + str(len(net_rows)))
    print("  networks median/worst : " + format(float(np.median(rn)), ".3e") + " / "
          + format(float(rn.max()), ".3e"))
print()
if rows and max(r["rel_T"] for r in rows) < 1e-6:
    print("  The L1 closed forms are confirmed against a model containing no equations of")
    print("  motion.  Finding 027 established they are right about the physics as stated;")
    print("  this establishes the physics as stated is what the components express.")

(OUT / "modelica_l1_full.json").write_text(json.dumps(
    {"skyhook": rows, "networks": net_rows}, indent=1), encoding="utf-8")
print()
print("wrote runs/modelica_l1_full.json")
