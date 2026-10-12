import _bootstrap  # noqa: F401
import numpy as np
from ecdr.l0 import G, TunedMassDamper, IsolationTask

task = IsolationTask("T_base", 50.0, -20.0, 3.0, 1.0e-3)
wn1 = float(np.sqrt(G / task.delta_max))
mech = TunedMassDamper()
prm = (wn1, 0.5, 0.05, 1.0, 0.2)
print("wn1 =", wn1, " prm =", prm)
print()
print("   w        |T|          asym        ratio")
for wv in [1e2, 3e2, 1e3, 1e4, 1e5, 1e6]:
    T = float(np.abs(mech.transmissibility(np.array([wv]), prm))[0])
    r = wv / wn1
    asym = 1.0 / ((1.0 - 0.05) * r ** 2)
    print(format(wv, "9.1e") + format(T, "12.6e") + format(asym, "12.6e") + format(T / asym, "12.4f"))

# what does a plain array call return?
w = np.array([1e3, 1e4, 1e5])
print()
print("array call shape:", np.shape(mech.transmissibility(w, prm)))
print("array call:", np.abs(mech.transmissibility(w, prm)))
print("loop call :", [float(np.abs(mech.transmissibility(np.array([v]), prm))[0]) for v in w])
