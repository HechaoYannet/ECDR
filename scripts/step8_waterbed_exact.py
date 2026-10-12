"""Step 8 - waterbed budget, ALL evaluation through the well-conditioned route.

Every trap hit so far came from evaluating the transfer function through the
determinant-expansion coefficients, whose dynamic range makes near-cancellation
unavoidable.  Here the polynomials are used ONLY to generate candidate
frequencies; every magnitude is evaluated with the mechanism 2x2 solve.
"""
import _bootstrap  # noqa: F401
import json
import pathlib
import numpy as np

from ecdr.l0 import G, IsolationTask, PassiveSDOF, TunedMassDamper
from ecdr.l0.invariants import tf_coeffs
from ecdr.l0.peaks import peak_of

line = "=" * 78


def w_amp_of(tf, w_hi, n=60001, u_lo=-24.0):
    """int_0^{w_hi} ln|T|/w^2 dw, evaluated with the caller transfer function."""
    u = np.linspace(u_lo, np.log(w_hi), n)
    T = np.abs(tf(np.exp(u)))
    return float(np.trapezoid(np.log(T) * np.exp(-u), u))


task = IsolationTask("T_base", 50.0, -20.0, 3.0, 1.0e-3)
wn_min = float(np.sqrt(G / task.delta_max))
floor = abs(np.log(task.T_iso)) / task.omega_low
m1, m2 = PassiveSDOF(), TunedMassDamper()
print(line)
print("T_base: floor = " + format(floor, ".8f") + "   A_max = " + format(task.A_max, ".6f"))
print(line)

print()
print(line)
print("SANITY: with the absorber switched off, M2 must reproduce M1 exactly")
print(line)
for z in (0.5432, 0.6, 1.0):
    f1 = (lambda w, z=z: m1.transmissibility(w, (wn_min, z)))
    f2 = (lambda w, z=z: m2.transmissibility(w, (wn_min, z, 1e-7, 1.0, 0.5)))
    a1 = w_amp_of(f1, task.omega_low)
    a2 = w_amp_of(f2, task.omega_low)
    print("  zeta=" + format(z, ".4f") + "   M1 W_amp=" + format(a1, ".8f")
          + "   M2(mu=1e-7) W_amp=" + format(a2, ".8f") + "   rel diff=" + format(abs(a1 - a2) / a1, ".2e"))

print()
print(line)
print("M1 passive SDOF, omega_n = wn_min, peak from the exact routine")
print(line)
best1 = (-np.inf, None)
n1 = 0
for z in np.linspace(0.5426, 4.0, 4000):
    num = [2 * z * wn_min, wn_min ** 2]
    den = [1.0, 2 * z * wn_min, wn_min ** 2]
    f = (lambda w, z=z: m1.transmissibility(w, (wn_min, z)))
    pk, _ = peak_of(f, num, den, n_grid=4000, refine=False)
    if pk > task.A_max * (1 + 1e-9):
        continue
    n1 += 1
    val = w_amp_of(f, task.omega_low)
    if val > best1[0]:
        best1 = (val, z)
print("  peak-feasible zeta count = " + str(n1))
print("  best W_amp = " + format(best1[0], ".8f") + " at zeta = " + format(best1[1], ".6f"))
v1 = "reaches the floor" if best1[0] >= floor else ("SHORT BY " + format(floor - best1[0], ".8f") + "  (" + format(100 * (1 - best1[0] / floor), ".2f") + " percent)")
print("  -> " + v1)

print()
print(line)
print("M2 passive chain, omega_n1 = wn_min")
print(line)
best2 = (-np.inf, None)
n2 = 0
n_tot = 0
vals = []
zetas1 = np.concatenate([np.logspace(-2.0, -0.7, 8), np.linspace(0.2, 1.0, 9)])
mus = np.concatenate([np.logspace(-3.5, -1.0, 9), np.linspace(0.1, 0.5, 5)])
ratios = np.logspace(-0.4, 1.0, 16)
zetas2 = np.concatenate([np.logspace(-1.5, -0.7, 6), np.linspace(0.2, 1.0, 6)])
for z1 in zetas1:
    for mu in mus:
        for ratio in ratios:
            for z2 in zetas2:
                n_tot += 1
                prm = (wn_min, float(z1), float(mu), float(ratio), float(z2))
                num, den = tf_coeffs("M2_tuned_mass_damper", prm)
                f = (lambda w, prm=prm: m2.transmissibility(w, prm))
                pk, _ = peak_of(f, num, den, n_grid=4000, refine=False)
                if pk > task.A_max * (1 + 1e-9):
                    continue
                n2 += 1
                val = w_amp_of(f, task.omega_low, n=20001)
                vals.append(val)
                if val > best2[0]:
                    best2 = (val, prm)
print("  examined " + str(n_tot) + " designs, " + str(n2) + " peak-feasible")
if best2[1] is None:
    print("  none peak-feasible")
else:
    print("  best  W_amp = " + format(best2[0], ".8f"))
    print("    zeta1=" + format(best2[1][1], ".6g") + " mu=" + format(best2[1][2], ".6g")
          + " ratio=" + format(best2[1][3], ".6g") + " zeta2=" + format(best2[1][4], ".6g"))
    if vals:
        print("    over the feasible set: min=" + format(min(vals), ".6f")
              + " median=" + format(float(np.median(vals)), ".6f") + " max=" + format(max(vals), ".6f"))
    v2 = "reaches the floor" if best2[0] >= floor else ("SHORT BY " + format(floor - best2[0], ".8f") + "  (" + format(100 * (1 - best2[0] / floor), ".2f") + " percent)")
    print("  -> " + v2)

print()
print(line)
print("M3 sky-hook")
print(line)
print("  total budget = -pi*zeta/wn; at zeta=2, wn=wn_min: " + format(-np.pi * 2.0 / wn_min, ".8f")
      + "  = " + format((-np.pi * 2.0 / wn_min) / (-floor), ".2f") + "x the demand")

out = pathlib.Path(__file__).resolve().parents[1] / "runs"
out.mkdir(exist_ok=True)
(out / "step8_waterbed_exact.json").write_text(json.dumps({
    "floor": floor, "wn_min": wn_min,
    "M1_best": best1[0], "M1_zeta": best1[1], "M1_n": n1,
    "M2_best": best2[0], "M2_params": best2[1], "M2_n": n2, "M2_total": n_tot,
}, indent=2, default=str), encoding="utf-8")
print()
print("wrote runs/step8_waterbed_exact.json")
