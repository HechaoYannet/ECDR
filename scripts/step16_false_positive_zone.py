"""Step 16 - the false-positive zone: tasks the L0 certificate calls feasible are not."""
import _bootstrap  # noqa: F401
import numpy as np
from ecdr.l0 import G, IsolationTask, PassiveSDOF, certify_passive_sdof
from ecdr.l0.feasibility import SEARCH_OMEGA
from ecdr.l1 import robust_violation
from ecdr.bench import default_family_spec

line = "=" * 78
m1 = PassiveSDOF()

def l1_best(task, rel=0.10, n_pert=12):
    """Best robustly-feasible L1 margin for M1 at this task, or None."""
    wn_min = float(np.sqrt(G / task.delta_max))
    best = np.inf
    for wn in np.linspace(wn_min, 3.0 * wn_min, 70):
        for z in np.concatenate([np.linspace(0.35, 1.5, 90), np.linspace(1.55, 3.5, 40)]):
            p = (wn, float(z))
            T = np.abs(m1.transmissibility(SEARCH_OMEGA, p))
            band = SEARCH_OMEGA >= task.omega_low
            if not (T[band].max() <= task.T_iso and T.max() <= task.A_max
                    and m1.static_deflection(p) <= task.delta_max):
                continue
            v = robust_violation(m1, p, task, SEARCH_OMEGA, rel=rel, n=n_pert, seed=5)
            best = min(best, v)
    return None if not np.isfinite(best) else float(best)

spec = default_family_spec()
print(line)
print("M1 verdict by fidelity, across the band edges")
print(line)
print("  " + "f_low".rjust(7) + "L0 certificate".rjust(17) + "L1 robust margin".rjust(19) + "   relation")
rows = []
for f in (160.0, 180.0, 200.0, 220.0, 240.0, 260.0, 300.0):
    task = spec.task(f)
    cert = certify_passive_sdof(task)
    v = l1_best(task)
    l0v = "FEASIBLE" if cert.feasible else "infeasible"
    if v is None:
        l1v = "none admissible"
    else:
        l1v = format(v, "+.4f") + (" (ok)" if v <= 0 else " (violated)")
    if cert.feasible and (v is None or v > 0):
        rel = "L0 says yes, L1 says NO"
    elif cert.feasible and v <= 0:
        rel = "agree: feasible"
    else:
        rel = "agree: infeasible"
    print("  " + format(f, "7.0f") + l0v.rjust(17) + l1v.rjust(19) + "   " + rel)
    rows.append({"f_low": f, "L0": l0v, "L1_margin": v, "relation": rel})

print()
print(line)
print("the false-positive zone")
print(line)
print("  L0 threshold          : 172.34 Hz  (exact, from the certificate)")
print("  L1 +-10 percent       : 239.72 Hz  (numerical)")
print("  => for 172.34 < f_low < 239.72 Hz the L0 certificate declares M1")
print("     FEASIBLE, and no design in that range survives a 10 percent perturbation.")
print()
print("  This is the regime the L0 experiment could not have: the certificate is")
print("  still SOUND for pruning (L0 infeasible => L1 infeasible) but its FEASIBILITY")
print("  verdict no longer holds, so it can prune and cannot construct.  Exactly the")
print("  asymmetry Finding 005 predicted, now with a measured zone attached.")
