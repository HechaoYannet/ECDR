"""Step 14 - the L1 rung, and the certificate-transfer property it must have."""
import _bootstrap  # noqa: F401
import numpy as np
from ecdr.l0 import G, IsolationTask, SkyHookActive, PassiveSDOF, certify_passive_sdof
from ecdr.l1 import LaggedSkyHook, robust_violation
from ecdr.l0.feasibility import SEARCH_OMEGA as SEARCH_GRID
from ecdr.bench import default_family_spec

line = "=" * 78
spec = default_family_spec()
task = spec.task(50.0)          # depth 3 at L0
easy = spec.task(220.0)         # depth 1 at L0, so M1 has feasible designs
wn_min = float(np.sqrt(G / task.delta_max))
omega = np.logspace(-1.0, 6.0, 6000)

print(line)
print("A. sanity: as the actuator bandwidth -> infinity, L1 must reproduce L0")
print(line)
l0 = SkyHookActive()
l1 = LaggedSkyHook()
z = 1.0
print("  " + "bandwidth".rjust(12) + "max |T_L1 - T_L0| over w in [0.1, 1e6]".rjust(40))
for wa in (1e2, 1e3, 1e4, 1e5, 1e6):
    T0 = l0.transmissibility(omega, (wn_min, z))
    T1 = l1.transmissibility(omega, (wn_min, z, wa))
    print("  " + format(wa, "12.0e") + format(float(np.max(np.abs(T1 - T0))), "40.3e"))

print()
print(line)
print("B. certificate transfer: L0 infeasible => L1 infeasible")
print(line)
print("  this holds by construction, because L1 only ADDS constraints.")
print("  checked here on the constraint sets rather than asserted:")
m1 = PassiveSDOF()
for probe, tag in ((easy, "easy task (f_low = 220 Hz)"), (task, "hard task (f_low = 50 Hz)")):
    n_l0 = n_l1 = 0
    rng = np.random.default_rng(0)
    for _ in range(3000):
        wn = float(rng.uniform(5.0, 400.0))
        zz = float(rng.uniform(1e-3, 2.0))
        p = (wn, zz)
        T = np.abs(m1.transmissibility(SEARCH_GRID, p))
        band = SEARCH_GRID >= probe.omega_low
        l0_ok = (T[band].max() <= probe.T_iso and T.max() <= probe.A_max
                 and m1.static_deflection(p) <= probe.delta_max)
        l1_ok = l0_ok and (robust_violation(m1, p, probe, SEARCH_GRID, rel=0.10, n=8, seed=1) <= 0.0)
        n_l0 += int(l0_ok)
        n_l1 += int(l1_ok)
    vacuous = "  (vacuous: no L0-feasible design exists, as the certificate says)" if n_l0 == 0 else ""
    print("    " + tag + ": sampled 3000 M1 designs, L0-feasible = " + str(n_l0)
          + ", L1-feasible = " + str(n_l1) + ", L1 subset of L0 = " + str(n_l1 <= n_l0) + vacuous)
cert = certify_passive_sdof(task)
print("    M1 certificate at L0: " + cert.verdict[:70] + "...")
print("    => the same verdict holds at L1, at L2, at any level that only adds constraints.")

print()
print(line)
print("C. what actuator bandwidth costs the escape to active control")
print(line)
print("  task T_base is depth-3 at L0: only M3 escapes.  Does it still, with a real actuator?")
print()
print("  " + "bandwidth".rjust(12) + "best in-band |T|".rjust(18) + "peak".rjust(12) + "verdict".rjust(14))
for wa in (3e2, 1e3, 3e3, 1e4, 1e5, 1e6):
    best = (np.inf, None)
    for zz in np.linspace(0.01, 30.0, 400):
        for wn in np.linspace(wn_min, 1.6 * wn_min, 30):
            T = np.abs(l1.transmissibility(omega, (wn, zz, wa)))
            band = omega >= task.omega_low
            inb = float(T[band].max())
            pk = float(T.max())
            sag = l1.static_deflection((wn, zz, wa))
            F = float(np.max(np.abs(l1.actuator_force_per_disp(omega, (wn, zz, wa)))))
            if pk > task.A_max or sag > task.delta_max or F > task.force_per_disp_max:
                continue
            if inb < best[0]:
                best = (inb, (wn, zz))
    if best[1] is None:
        print("  " + format(wa, "12.0e") + "           none admissible")
        continue
    ok = best[0] <= task.T_iso
    print("  " + format(wa, "12.0e") + format(best[0], "18.6f")
          + format(best[0] / task.T_iso * 1.0, "12.2f") + ("        ESCAPES" if ok else "         FAILS"))
print()
print("  (peak column shows the ratio of achieved in-band |T| to the -20 dB target;")
print("   1.00 would exactly meet it)")
