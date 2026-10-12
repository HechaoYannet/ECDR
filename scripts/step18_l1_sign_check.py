"""Reproduce the reported L1 sign defect, and confirm the fix."""
import _bootstrap  # noqa: F401
import numpy as np
from ecdr.bench import default_family_spec
from ecdr.l0 import PassiveSDOF
from ecdr.l1 import MechanismProblemL1, verify_l1

task = default_family_spec().task(210.0)
mech = PassiveSDOF()
x = np.array([111.86361, 0.590427])
rel, n_pert, seed = 0.06, 5, 0

p = MechanismProblemL1(task, mech, rel=rel, n_pert=n_pert, seed=seed)
print("task:", task.name, "  T_iso =", task.T_iso)
print("design x =", x)
print()
band = p.grid >= task.omega_low
vals = []
for d in p._dirs:
    q = np.clip(x * d, p._lo, p._hi)
    T = np.abs(mech.transmissibility(p.grid, q))
    vals.append(float(T[band].max()))
print("per-direction in-band |T|:", [round(v, 6) for v in vals])
print("  min =", round(min(vals), 6), "  max =", round(max(vals), 6))
print()
obj, cons = p.evaluate(x)
print("evaluate() objective      =", round(obj, 6), "  -> in-band", round(-obj, 6))
print("expected after the fix    = -", round(max(vals), 6), " (the worst direction)")
print("peak/sag/force violations =", [round(float(c), 6) for c in cons])
print()
v = verify_l1(mech, x, task, rel=rel, n_pert=24)
print("verify_l1 (independent, 24 directions):")
print("  worst_in_band_T =", round(v["worst_in_band_T"], 6), " limit =", v["limit"])
print("  meets target    =", v["meets_isolation_target"])
print()
ok = abs(-obj - max(vals)) < 1e-12
print("FIX VERIFIED: evaluate() now returns the worst direction:", ok)
