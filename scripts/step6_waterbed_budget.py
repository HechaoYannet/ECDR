"""Step 6 - the waterbed budget as a necessary condition for passive mechanisms.

Reasoning
---------
For ANY passive mechanism in the family the exact invariant gives

    W_iso + W_amp = 0,   W_iso = int_{w_low}^inf ln|T|/w^2 dw
                         W_amp = int_0^{w_low}  ln|T|/w^2 dw

The band constraint |T| <= T_iso on [w_low, inf) forces W_iso <= ln(T_iso)/w_low,
hence

    W_amp >= |ln T_iso| / w_low        ("the floor")

So a passive mechanism is feasible ONLY IF it can raise its low-frequency
amplification integral to the floor while keeping the peak under A_max.  If the
largest achievable W_amp is below the floor, the mechanism is infeasible.  This
needs no rate assumption: the floor is a number and the maximum is a number.

Scaling reduction
-----------------
T depends on omega_n1 only through r = w/omega_n1, so

    W_amp = (1/omega_n1) * int_0^{w_low/omega_n1} ln|T(r)|/r^2 dr

which is decreasing in omega_n1.  The sag constraint gives omega_n1 >= wn_min,
so the maximum sits exactly at omega_n1 = wn_min and one dimension disappears.
"""
import _bootstrap  # noqa: F401
import json
import pathlib
import numpy as np

from ecdr.l0 import G, IsolationTask, PassiveSDOF, TunedMassDamper
from ecdr.l0.invariants import tf_coeffs

line = "=" * 78
omega_low = None


def w_amp(num, den, w_hi, n=20001, u_lo=-20.0):
    u = np.linspace(u_lo, np.log(w_hi), n)
    s = 1j * np.exp(u)
    T = np.polyval(num, s) / np.polyval(den, s)
    return float(np.trapezoid(np.log(np.abs(T)) * np.exp(-u), u))


task = IsolationTask("T_base", 50.0, -20.0, 3.0, 1.0e-3)
wn_min = float(np.sqrt(G / task.delta_max))
floor = abs(np.log(task.T_iso)) / task.omega_low
print(line)
print("T_base: the waterbed floor a passive mechanism must reach")
print(line)
print("  omega_low = " + format(task.omega_low, ".4f") + " rad/s,  wn_min = " + format(wn_min, ".4f") + " rad/s")
print("  floor = |ln T_iso| / omega_low = " + format(floor, ".8f"))
print("  peak limit A_max = " + format(task.A_max, ".6f"))

w_peak = np.logspace(np.log10(0.05), np.log10(5.0e4), 2000)

print()
print(line)
print("M1 passive SDOF - full scan, omega_n free above wn_min")
print(line)
mech1 = PassiveSDOF()
best1 = (-np.inf, None)
n1 = 0
for wn in np.linspace(wn_min, 8.0 * wn_min, 160):
    for z in np.concatenate([np.linspace(0.40, 1.3, 180), np.linspace(1.35, 3.0, 40)]):
        T = np.abs(mech1.transmissibility(w_peak, (wn, z)))
        if T.max() > task.A_max:
            continue
        n1 += 1
        val = w_amp([2 * z * wn, wn ** 2], [1.0, 2 * z * wn, wn ** 2], task.omega_low)
        if val > best1[0]:
            best1 = (val, (wn, z))
print("  peak-feasible designs examined: " + str(n1))
print("  best W_amp = " + format(best1[0], ".8f") + "  at omega_n = "
      + format(best1[1][0], ".4f") + ", zeta = " + format(best1[1][1], ".6f"))
print("  -> " + ("budget satisfiable" if best1[0] >= floor else "SHORT BY " + format(floor - best1[0], ".8f")))

print()
print(line)
print("M2 passive chain - scan at omega_n1 = wn_min")
print(line)
mech2 = TunedMassDamper()
best2 = (-np.inf, None)
n2 = 0
zetas1 = np.logspace(-4.0, -0.12, 14)
mus = np.logspace(-4.5, -0.6, 14)
ratios = np.logspace(-0.4, 1.0, 16)
zetas2 = np.logspace(-3.0, -0.08, 12)
for z1 in zetas1:
    for mu in mus:
        for ratio in ratios:
            for z2 in zetas2:
                T = np.abs(mech2.transmissibility(w_peak, (wn_min, z1, mu, ratio, z2)))
                if T.max() > task.A_max:
                    continue
                n2 += 1
                num, den = tf_coeffs("M2_tuned_mass_damper", (wn_min, z1, mu, ratio, z2))
                val = w_amp(num, den, task.omega_low)
                if val > best2[0]:
                    best2 = (val, (wn_min, z1, mu, ratio, z2))
print("  peak-feasible designs examined: " + str(n2))
if best2[1] is None:
    print("  none found")
else:
    print("  best W_amp = " + format(best2[0], ".8f"))
    print("    zeta1 = " + format(best2[1][1], ".6g") + ", mu = " + format(best2[1][2], ".6g")
          + ", ratio = " + format(best2[1][3], ".6g") + ", zeta2 = " + format(best2[1][4], ".6g"))
    print("  -> " + ("budget satisfiable" if best2[0] >= floor else "SHORT BY " + format(floor - best2[0], ".8f")))

print()
print(line)
print("M3 sky-hook - the budget is not zero")
print(line)
print("  total = -pi*zeta/wn < 0, so the mechanism has net isolation room that the")
print("  passive classes simply do not have.  At zeta=2, wn=wn_min the total is "
      + format(-np.pi * 2.0 / wn_min, ".8f") + ".")

out = pathlib.Path(__file__).resolve().parents[1] / "runs"
out.mkdir(exist_ok=True)
(out / "step6_waterbed_budget.json").write_text(json.dumps({
    "task": "T_base", "floor": floor, "wn_min": wn_min,
    "M1_best_W_amp": best1[0], "M1_params": best1[1], "M1_examined": n1,
    "M2_best_W_amp": best2[0], "M2_params": best2[1], "M2_examined": n2,
}, indent=2, default=str), encoding="utf-8")
print()
print("wrote runs/step6_waterbed_budget.json")
