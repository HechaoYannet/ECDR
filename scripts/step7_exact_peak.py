"""Verify the rebuilt peak routine against dense brute-force scans."""
import _bootstrap  # noqa: F401
import numpy as np
from ecdr.l0.invariants import tf_coeffs
from ecdr.l0.peaks import peak_of
from ecdr.l0.certificates import peak_transmissibility_sdof, peak_transmissibility_skynook
from ecdr.l0 import TunedMassDamper, PassiveSDOF, SkyHookActive

line = "=" * 78
print(line)
print("A. regression against the closed forms")
print(line)
wa = wb = 0.0
for z in (0.02, 0.05, 0.1, 0.2, 0.354, 0.5426, 0.6, 0.7071, 0.9, 1.5):
    wn = 99.03
    f1 = lambda w, wn=wn, z=z: PassiveSDOF().transmissibility(w, (wn, z))
    f3 = lambda w, wn=wn, z=z: SkyHookActive().transmissibility(w, (wn, z))
    a, _ = peak_of(f1, [2 * z * wn, wn ** 2], [1.0, 2 * z * wn, wn ** 2])
    b, _ = peak_of(f3, [wn ** 2], [1.0, 2 * z * wn, wn ** 2])
    wa = max(wa, abs(a - peak_transmissibility_sdof(z)))
    wb = max(wb, abs(b - peak_transmissibility_skynook(z)))
print("  worst |peak - closed| M1 = " + format(wa, ".3e") + "   M3 = " + format(wb, ".3e"))

print()
print(line)
print("B. sharp resonances: routine vs dense brute-force scan")
print(line)
mech2 = TunedMassDamper()
wn_min = 99.0285
cases = [
    ((wn_min, 0.001, 0.000316228, 10.0, 0.0196023), 95.0, 105.0),
    ((wn_min, 0.002, 0.01, 1.0, 0.02), 90.0, 110.0),
    ((wn_min, 0.005, 0.05, 1.0, 0.1), 80.0, 130.0),
    ((wn_min, 0.02, 0.1, 1.0, 0.2), 60.0, 200.0),
    ((wn_min, 0.5, 0.2, 1.0, 0.3), 30.0, 400.0),
    ((wn_min, 0.457, 0.057, 0.744, 0.295), 30.0, 400.0),
]
worst_rel = 0.0
for prm, lo, hi in cases:
    num, den = tf_coeffs("M2_tuned_mass_damper", prm)
    f = lambda w, prm=prm: mech2.transmissibility(w, prm)
    pk, wp = peak_of(f, num, den)
    w = np.linspace(lo, hi, 2000001)
    T = np.abs(f(w))
    i = int(np.argmax(T))
    rel = abs(pk - T[i]) / max(T[i], 1e-300)
    worst_rel = max(worst_rel, rel)
    print("  zeta1=" + format(prm[1], ".4g") + " mu=" + format(prm[2], ".4g")
          + " ratio=" + format(prm[3], ".4g") + " zeta2=" + format(prm[4], ".4g"))
    print("      routine = " + format(pk, ".6f") + " at w=" + format(wp, ".5f")
          + "   dense(2e6) = " + format(T[i], ".6f") + " at w=" + format(w[i], ".5f")
          + "   rel = " + format(rel, ".2e"))
print("  worst relative difference = " + format(worst_rel, ".3e"))
