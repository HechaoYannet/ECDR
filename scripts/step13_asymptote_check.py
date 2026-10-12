"""Does the high-frequency asymptote bound |T| from below?  (If so, M2 is provable.)"""
import _bootstrap  # noqa: F401
import numpy as np
from ecdr.l0 import G, TunedMassDamper, IsolationTask
from ecdr.l0.invariants import tf_coeffs

task = IsolationTask("T_base", 50.0, -20.0, 3.0, 1.0e-3)
wn1 = float(np.sqrt(G / task.delta_max))
mech = TunedMassDamper()

# candidate designs spanning heavy and light absorber damping
cases = [
    (0.5, 0.05, 1.0, 0.2),
    (0.5, 0.05, 1.0, 0.02),
    (0.1, 0.05, 1.0, 0.5),
    (0.457, 0.057, 0.744, 0.295),
    (0.25, 0.2, 1.0, 0.8),
    (0.9, 0.01, 1.0, 0.9),
]

print("compare |T| with the leading asymptote k1/(m1 w^2) at high frequency")
print("  (k1/(m1 w^2) = 1/((1-mu) r^2) with r = w/wn1)")
print()
w = np.logspace(3.0, 5.5, 400)
r = w / wn1
for z1, mu, ratio, z2 in cases:
    prm = (wn1, z1, mu, ratio, z2)
    T = np.abs(mech.transmissibility(w, prm))
    asym = 1.0 / ((1.0 - mu) * r ** 2)
    rel = T / asym
    print("  zeta1=" + format(z1, ".3g") + " mu=" + format(mu, ".3g")
          + " ratio=" + format(ratio, ".3g") + " zeta2=" + format(z2, ".3g")
          + "   |T|/asymptote: min=" + format(rel.min(), ".4f")
          + " max=" + format(rel.max(), ".4f"))

print()
print("interpretation: a ratio ABOVE 1 means the asymptote is a lower bound")
print("(which would let us prove M2 infeasible); BELOW 1 means an upper bound,")
print("in which case the asymptote route is closed.")
