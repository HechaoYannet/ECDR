"""Step 62 - the lagged sky-hook through Modelica, one case.

emit_skyhook_model declares a payload mass, a support spring, an ideal sky-hook gain of
-c_sky on the payload velocity, a first-order lag, and a Force source applying the result.
No differentiator and no equation of motion appears.  If the linearized transfer from ground
displacement to payload displacement matches the L1 closed form, then the L1 expressions of
Finding 027 - until now confirmed only against an integration of the SAME equations - are
confirmed against equations this project did not write.
"""
import _bootstrap  # noqa: F401
import json
import pathlib

import numpy as np

from ecdr.l1.models import LaggedSkyHook
from ecdr.l2.modelica.emit import emit_skyhook_model
from ecdr.l2.modelica.linearize import linearize, tf_mag

line = "=" * 92
wn, z, wa = 60.0, 0.5, 60.0
mech = LaggedSkyHook()

print(line)
print("emitting and linearizing:  omega_n = " + format(wn, ".4g")
      + ",  zeta = " + format(z, ".4g") + ",  omega_a = " + format(wa, ".4g"))
print(line)
model = emit_skyhook_model(wn, z, wa, 1.0, name="SkyTest")
M = linearize(model, name="SkyTest")
if not M["ok"]:
    print("  LINEARIZATION FAILED")
    print("  " + M["log"][-1200:].replace("\n", "\n  "))
    raise SystemExit(0)
print("  states " + str(M["n"]) + ", inputs " + str(M["m"]) + ", outputs " + str(M["p"]))
print("  B = " + np.array2string(M["B"].ravel(), precision=4, separator=", "))

omegas = np.array([0.25 * wn, 1.0 * wn, 3.0 * wn])
print()
print("  " + "omega".rjust(11) + "|T| L1 closed".rjust(18) + "|T| Modelica".rjust(18)
      + "ratio".rjust(11) + "|F| L1 closed".rjust(18) + "|F| Modelica".rjust(18) + "ratio".rjust(11))

rows = []
for w in omegas:
    refT = float(np.abs(mech.transmissibility(np.array([w]), (wn, z, wa)))[0])
    refF = float(np.abs(mech.actuator_force_per_disp(np.array([w]), (wn, z, wa)))[0])
    rT = tf_mag(M, np.array([w]))[0]
    Ah, Bh, Ch, Dh = M["A"], M["B"], M["C"], M["D"]
    r = Ch @ np.linalg.solve(1j * w * np.eye(Ah.shape[0]) - Ah, Bh) + Dh
    gotT, gotF = abs(r[0, 0]), abs(r[1, 0])
    rows.append({"omega": float(w), "T_L1": refT, "T_mod": float(gotT),
                 "F_L1": refF, "F_mod": float(gotF)})
    print("  " + format(w, ".5g").rjust(11) + format(refT, ".8e").rjust(18)
          + format(gotT, ".8e").rjust(18) + format(gotT / refT, ".6f").rjust(11)
          + format(refF, ".8e").rjust(18) + format(gotF, ".8e").rjust(18)
          + format(gotF / refF, ".6f").rjust(11))

print()
print(line)
print("VERDICT")
print(line)
rT = np.array([r["T_mod"] / r["T_L1"] for r in rows])
rF = np.array([r["F_mod"] / r["F_L1"] for r in rows])
print("  |T| ratio  : " + ", ".join(format(v, ".6f") for v in rT))
print("  |F| ratio  : " + ", ".join(format(v, ".6f") for v in rF))
print()
if abs(rT.max() - 1) < 1e-3 and abs(rT.min() - 1) < 1e-3:
    print("  MATCH for the transmissibility.")
else:
    print("  transmissibility MISMATCH - check the sign convention on the Force source.")
if abs(rF.max() - 1) < 1e-3 and abs(rF.min() - 1) < 1e-3:
    print("  MATCH for the actuator force.")
else:
    print("  actuator force MISMATCH.")

out = pathlib.Path(__file__).resolve().parents[1] / "runs"
(out / "modelica_skyhook.json").write_text(json.dumps({"rows": rows}, indent=1), encoding="utf-8")
print()
print("wrote runs/modelica_skyhook.json")
