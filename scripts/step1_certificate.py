"""Step 1 - check that the closed-form M1 infeasibility certificate is sound.

Independent checks:
  A. the monotonicity assumptions F1-F3 the proof relies on
  B. the closed-form r* against a numerical root find of T(r) = T_iso
  C. falsification.  When the certificate says INFEASIBLE, no cell of a dense
     (omega_n, zeta) grid may be feasible.  When it says FEASIBLE, the witness it
     constructs must actually satisfy every constraint.
"""
import _bootstrap  # noqa: F401
import numpy as np
from scipy.optimize import brentq

from ecdr.l0 import (
    G, IsolationTask, PassiveSDOF,
    certify_passive_sdof, r_star, zeta_min_from_peak,
    constraint_violation, verify_monotonicity,
)
from ecdr.l0.certificates import transmissibility_sdof, peak_transmissibility_sdof

np.set_printoptions(precision=6, suppress=True)
line = "=" * 78

print(line)
print("A. monotonicity assumptions F1-F3 (worst observed violation; all must be ~0)")
print(line)
for k, v in verify_monotonicity(seed=7).items():
    print(f"  {k:40s} {v: .3e}")

print()
print(line)
print("B. closed-form r* vs numerical root of T(r) = T_iso")
print(line)
worst = 0.0
for z in (0.05, 0.1, 0.2, 0.383229, 0.5):
    for T_iso in (0.2, 0.1, 0.05):
        closed = r_star(z, T_iso)
        num = brentq(lambda r: transmissibility_sdof(r, z) - T_iso, 1.0 + 1e-9, 1e4)
        worst = max(worst, abs(closed - num))
print(f"  checked 15 (zeta, T_iso) combinations; worst |closed - numeric| = {worst:.3e}")

print()
print(line)
print("C. falsification over a dense (omega_n, zeta) grid")
print(line)
mech = PassiveSDOF()
omega = np.logspace(np.log10(0.5), np.log10(20000.0), 8000)

cases = [
    (50.0, -20.0, 3.0, 1.0),
    (60.0, -20.0, 3.0, 1.0),
    (100.0, -20.0, 3.0, 1.0),
    (150.0, -20.0, 3.0, 1.0),
    (50.0, -20.0, 12.0, 1.0),
    (80.0, -20.0, 6.0, 1.0),
    (50.0, -14.0, 6.0, 0.5),
]
all_ok = True
for f_low, T_iso_db, A_max_db, delta_mm in cases:
    task = IsolationTask("probe", f_low, T_iso_db, A_max_db, delta_mm / 1e3)
    cert = certify_passive_sdof(task)

    if not cert.feasible:
        wn_min = np.sqrt(G / task.delta_max)
        wns = np.linspace(0.1 * wn_min, 8.0 * wn_min, 260)
        zs = np.concatenate([np.linspace(1e-4, 0.2, 90), np.linspace(0.2, 1.5, 90)])
        best = min(constraint_violation(mech, (wn, z), task, omega) for wn in wns for z in zs)
        shown = f"grid best violation = {best: .4f}"
        ok = best > 0.0
    else:
        # the certificate's own witness must satisfy every constraint
        wit = (cert.omega_n_max_allowed, cert.zeta_min)
        best = constraint_violation(mech, wit, task, omega)
        shown = f"witness violation   = {best: .4f}"
        ok = best <= 1e-9
    all_ok &= ok
    print(f"  f_low={f_low:5.0f} Hz  A_max={A_max_db:+4.0f} dB  delta={delta_mm:.1f} mm  "
          f"Lambda={cert.Lambda:7.4f}  cert={'FEASIBLE  ' if cert.feasible else 'INFEASIBLE'}  "
          f"{shown}  {'ok' if ok else '*** FAIL ***'}")

print()
print(f"  overall: {'ALL CHECKS PASS' if all_ok else '*** SOME CHECKS FAILED ***'}")

print()
print(line)
print("D. the reference escape task")
print(line)
task = IsolationTask(name="T_base", f_low=50.0, T_iso_db=-20.0, A_max_db=3.0, delta_max=1.0e-3)
cert = certify_passive_sdof(task)
print(task.describe())
print()
print(cert.report())
print()
print(f"  zeta_min(M1, feedthrough)     = {zeta_min_from_peak(cert.A_max if False else task.A_max, peak_transmissibility_sdof):.6f}")
from ecdr.l0.certificates import peak_transmissibility_skynook, zeta_min_from_peak as zmp
print(f"  zeta_min(sky-hook, no feedthr) = {zmp(task.A_max, peak_transmissibility_skynook):.6f}")
print("  -> the passive mechanism needs more damping for the same peak budget,")
print("     and more damping makes its high-frequency isolation worse (F3).")

crit = brentq(lambda f: certify_passive_sdof(IsolationTask("c", f, -20.0, 3.0, 1.0e-3)).Lambda - 1.0,
              20.0, 400.0)
print(f"\n  critical f_low where Lambda = 1: {crit:.2f} Hz")
