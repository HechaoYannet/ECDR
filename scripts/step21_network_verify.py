"""Verify the general network evaluator against the hand-written L0 mechanisms.

If the general evaluator does not reproduce M1 and M2 exactly, nothing built on it is
trustworthy, so this runs before any ensemble work.
"""
import _bootstrap  # noqa: F401
import numpy as np

from ecdr.l0 import PassiveSDOF, TunedMassDamper
from ecdr.structure import Structure

omega = np.logspace(-1, 5, 400)
line = "=" * 78
print(line)
print("A. network evaluator vs the hand-written L0 models")
print(line)

# --- M1: one mass, spring+damper to ground --------------------------------
wn, z = 99.03, 0.5426
m1 = 1.0
k1 = wn ** 2 * m1
c1 = 2 * z * wn * m1
s1 = Structure(masses=np.array([m1]), springs={}, dampers={},
               ground_k={0: k1}, ground_c={0: c1})
ref = PassiveSDOF().transmissibility(omega, (wn, z))
got = s1.transmissibility(omega)
print("  M1 max abs diff T        : " + format(float(np.max(np.abs(got - ref))), ".3e"))
print("  M1 static deflection     : net=" + format(s1.static_deflection(), ".10f")
      + "  ref=" + format(9.80665 / wn ** 2, ".10f")
      + "  diff=" + format(abs(s1.static_deflection() - 9.80665 / wn ** 2), ".2e"))

# --- M2: tuned mass damper -------------------------------------------------
wn1, z1, mu, ratio, z2 = 99.03, 0.457, 0.057, 0.744, 0.295
M = 1.0
m1v = M * (1 - mu)
m2v = M * mu
wn2 = ratio * wn1
k1v = wn1 ** 2 * M
c1v = 2 * z1 * np.sqrt(k1v * M)
k2v = wn2 ** 2 * m2v
c2v = 2 * z2 * np.sqrt(k2v * m2v)
s2 = Structure(masses=np.array([m1v, m2v]), springs={(0, 1): k2v}, dampers={(0, 1): c2v},
               ground_k={0: k1v}, ground_c={0: c1v})
ref2 = TunedMassDamper().transmissibility(omega, (wn1, z1, mu, ratio, z2))
got2 = s2.transmissibility(omega)
print("  M2 max abs diff T        : " + format(float(np.max(np.abs(got2 - ref2))), ".3e"))
print("  M2 static deflection     : net=" + format(s2.static_deflection(), ".10f")
      + "  ref=" + format(9.80665 / wn1 ** 2, ".10f")
      + "  diff=" + format(abs(s2.static_deflection() - 9.80665 / wn1 ** 2), ".2e"))

ok = (np.max(np.abs(got - ref)) < 1e-10 and np.max(np.abs(got2 - ref2)) < 1e-10
      and abs(s1.static_deflection() - 9.80665 / wn ** 2) < 1e-10
      and abs(s2.static_deflection() - 9.80665 / wn1 ** 2) < 1e-10)
print()
print("  VERDICT: general evaluator reproduces both L0 mechanisms exactly:", ok)
