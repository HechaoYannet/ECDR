"""Step 2 - is the provably-infeasible task actually escapable?

For a task to be a valid Design-Space Escape Task it needs both halves:
  * the initial mechanism is provably inadequate  (certificate, exact for M1)
  * some other mechanism class demonstrably works (witness, existence by construction)

This script establishes both and reports the escape ladder.
"""
import _bootstrap  # noqa: F401
import numpy as np

from ecdr.l0 import (
    G, IsolationTask, PassiveSDOF, TunedMassDamper, SkyHookActive,
    certify_passive_sdof, constraint_violation, search_witness,
)

line = "=" * 78
np.set_printoptions(precision=6, suppress=True)


def make_task(name, f_low, T_iso_db=-20.0, A_max_db=3.0, delta_mm=1.0, force_budget=None):
    delta = delta_mm / 1e3
    fmax = None if force_budget is None else force_budget * (G / delta)
    return IsolationTask(name, f_low, T_iso_db, A_max_db, delta, fmax)


task = make_task("T_base", 50.0, force_budget=2.0)

print(line)
print("TASK")
print(line)
print(task.describe())
wn_min = np.sqrt(G / task.delta_max)
print(f"  reference quantities: omega_n_min = {wn_min:.2f} rad/s, omega_n_min^2 = {wn_min**2:.1f} 1/s^2")
print(f"  actuator budget = {task.force_per_disp_max:.1f} 1/s^2 = {task.force_per_disp_max / wn_min**2:.1f} x omega_n_min^2")

print()
print(line)
print("M1  passive SDOF  - analytic certificate")
print(line)
cert = certify_passive_sdof(task)
print(cert.report())

print()
print(line)
print("M2  tuned mass damper  - witness search (5 parameters)")
print(line)
m2 = TunedMassDamper()
res2 = search_witness(m2, task, seed=1, maxiter=250, popsize=25)
print(f"  witness found : {res2['witness_found']}")
print(f"  violation     : {res2['violation']:+.5f}   (<= 0 means every constraint holds)")
print(f"  params        : " + ", ".join(f"{k}={v:.6g}" for k, v in res2["params"].items()))
for k, v in res2["constraint_report"].items():
    print(f"    {k:28s} {v:.6g}")

print()
print(line)
print("M3  sky-hook active  - witness search (2 parameters)")
print(line)
m3 = SkyHookActive()
res3 = search_witness(m3, task, seed=1, maxiter=250, popsize=40)
print(f"  witness found : {res3['witness_found']}")
print(f"  violation     : {res3['violation']:+.5f}")
print(f"  params        : " + ", ".join(f"{k}={v:.6g}" for k, v in res3["params"].items()))
for k, v in res3["constraint_report"].items():
    print(f"    {k:28s} {v:.6g}")

print()
print(line)
print("ESCAPE LADDER")
print(line)
print(f"  M1 passive SDOF      : {'FEASIBLE' if cert.feasible else 'PROVABLY INFEASIBLE'}  (Lambda = {cert.Lambda:.4f})")
print(f"  M2 tuned mass damper : {'FEASIBLE (witness)' if res2['witness_found'] else 'no witness found'}")
print(f"  M3 sky-hook active   : {'FEASIBLE (witness)' if res3['witness_found'] else 'no witness found'}")
