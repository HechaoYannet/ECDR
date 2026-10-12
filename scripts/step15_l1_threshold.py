"""Step 15 - does L1 robustness move the passive-SDOF feasibility threshold?

At L0 the M1 threshold is exactly 172.237063 Hz.  If requiring the design to hold
across +-10 percent parameter perturbation moves that threshold a long way, then
L0 feasibility near the boundary is an artefact of the model, and the fidelity
ladder is doing real work rather than decorating the result.
"""
import _bootstrap  # noqa: F401
import json, pathlib
import numpy as np
from scipy.optimize import brentq
from ecdr.l0 import G, IsolationTask, PassiveSDOF, certify_passive_sdof
from ecdr.l0.feasibility import SEARCH_OMEGA
from ecdr.l1 import robust_violation

line = "=" * 78
m1 = PassiveSDOF()

def l0_feasible(task, p):
    T = np.abs(m1.transmissibility(SEARCH_OMEGA, p))
    band = SEARCH_OMEGA >= task.omega_low
    return (T[band].max() <= task.T_iso and T.max() <= task.A_max
            and m1.static_deflection(p) <= task.delta_max)

def robust_feasible(task, rel, n_pert, seed):
    wn_min = float(np.sqrt(G / task.delta_max))
    for wn in np.linspace(wn_min, 3.0 * wn_min, 70):
        for z in np.concatenate([np.linspace(0.35, 1.5, 90), np.linspace(1.55, 3.5, 40)]):
            p = (wn, float(z))
            if not l0_feasible(task, p):
                continue
            if robust_violation(m1, p, task, SEARCH_OMEGA, rel=rel, n=n_pert, seed=seed) <= 0.0:
                return True, p
    return False, None

spec_rel = [(0.0, 1, "L0 (no perturbation)"), (0.05, 8, "L1 +-5 percent"), (0.10, 12, "L1 +-10 percent")]
print(line)
print("passive-SDOF feasibility threshold vs robustness requirement")
print(line)
print("  " + "requirement".ljust(24) + "threshold (Hz)".rjust(16))
results = {}
for rel, n_pert, tag in spec_rel:
    def ok(f):
        task = IsolationTask("probe", f, -20.0, 3.0, 1.0e-3)
        if rel == 0.0:
            return certify_passive_sdof(task).feasible
        return robust_feasible(task, rel, n_pert, seed=3)[0]
    lo, hi = 150.0, 900.0
    if ok(hi):
        thr = brentq(lambda f: (1.0 if ok(f) else 0.0) - 0.5, lo, hi, xtol=0.5)
        results[tag] = thr
        print("  " + tag.ljust(24) + format(thr, "16.2f"))
    else:
        results[tag] = None
        print("  " + tag.ljust(24) + "        > 900")

print()
print(line)
print("interpretation")
print(line)
base = results.get("L0 (no perturbation)")
for tag, thr in results.items():
    if thr is None or base is None:
        continue
    print("  " + tag.ljust(24) + "shift vs L0 = " + format(thr - base, "+8.2f") + " Hz")
print()
print("  A large shift means the L0-feasible designs near the boundary are model")
print("  artefacts: they satisfy the equations but not the engineering requirement.")
print("  That is the argument for the fidelity ladder being load-bearing rather than")
print("  decorative, and it is measurable, not rhetorical.")

out = pathlib.Path(__file__).resolve().parents[1] / "runs"
out.mkdir(exist_ok=True)
(out / "l1_threshold.json").write_text(json.dumps(results, indent=1, default=str), encoding="utf-8")
print()
print("wrote runs/l1_threshold.json")
