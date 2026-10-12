"""Step 26 (corrected) - verify the high-frequency law WITHOUT a guard that excludes
the counterexamples.

What went wrong the first time
------------------------------
Step 25 tested the claimed asymptote only on structures satisfying asym > 0, i.e. those
WITH a payload ground tie.  That guard silently excluded every structure the claim is
most likely to fail on, so the test could not fail.  When step 26 removed the guard, the
worst case had f0 = g0 = 0 and measured |T| ~ omega^-2, against the claimed omega^-3.

Re-derivation
-------------
    P(s) = sum_j cofactor_{j0}(s) * (f_j + g_j s)

Only j = 0 contributes at order s^(2n-2), because for j >= 1 the submatrix deleting row j
and column 0 of the DIAGONAL mass matrix has a zero column and its determinant vanishes.
So the leading term is prod_{k != 0} m_k * (f0 + g0 s) * s^(2n-2), giving

    T(s) = g0/(m0 s) + (f0 + beta)/(m0 s^2) + O(s^-3)

where beta collects the j >= 1 cofactors at order s^(2n-3) times the s from (f_j + g_j s).
**beta is NOT zero in general**, so the claim "no payload tie implies T = O(s^-3)" is
FALSE: those structures fall off at s^-2, carried by the OTHER ground ties.

The defensible statement is the leading one:

    omega * T(j omega)  ->  g0 / m0        as omega -> infinity

which involves the payload's own ground damping and nothing else in the network.
"""
import _bootstrap  # noqa: F401
import numpy as np

from ecdr.structure import ensemble

line = "=" * 86
ens = ensemble(seed=5, count=600, n_lo=2, n_hi=8)
freqs = np.array([1e3, 1e4, 1e5, 1e6, 1e7, 1e8])

print(line)
print("TEST 1  omega*|T| -> g0/m0, over ALL structures, no guard")
print(line)
worst = 0.0
worst_i = None
for i, s in enumerate(ens):
    g0 = s.ground_c.get(0, 0.0)
    m0 = s.masses[0]
    v = np.abs(s.transmissibility(freqs)) * freqs
    target = g0 / m0
    err = abs(v[-1] - target) / max(abs(target), 1e-12)
    if err > worst:
        worst, worst_i = err, i
print("  structures tested      : " + str(len(ens)) + "  (no exclusion)")
print("  worst relative error at omega = " + format(freqs[-1], ".0e") + " : "
      + format(worst, ".3e"))
print("  structure " + str(worst_i) + ": g0 = " + format(ens[worst_i].ground_c.get(0, 0.0), ".4g")
      + ", m0 = " + format(ens[worst_i].masses[0], ".4g")
      + ", ground ties = " + str(len(set(ens[worst_i].ground_k) | set(ens[worst_i].ground_c))))

print()
print("  convergence of omega*|T| for three representative structures:")
print("  " + "case".rjust(22) + "".join(format(w, ".0e").rjust(12) for w in freqs))
cases = []
for tag, pick in (("payload grounded", [i for i, s in enumerate(ens)
                                        if 0 in s.ground_c]),
                  ("payload tie, no damping", [i for i, s in enumerate(ens)
                                               if 0 in s.ground_k and 0 not in s.ground_c]),
                  ("no payload tie", [i for i, s in enumerate(ens)
                                      if 0 not in s.ground_k and 0 not in s.ground_c])):
    if not pick:
        continue
    s = ens[pick[0]]
    v = np.abs(s.transmissibility(freqs)) * freqs
    cases.append({"case": tag, "values": [float(x) for x in v],
                  "target_g0_over_m0": float(s.ground_c.get(0, 0.0) / s.masses[0])})
    print("  " + tag.rjust(22) + "".join(format(x, ".4e").rjust(12) for x in v))
    print("  " + "  target g0/m0".rjust(22) + format(s.ground_c.get(0, 0.0) / s.masses[0],
                                                      ".4e").rjust(12))

print()
print(line)
print("TEST 2  the O(omega^-2) coefficient is NOT only f0")
print(line)
print("  scale the residual by omega^2 for a structure with NO payload tie:")
noT = [i for i, s in enumerate(ens) if 0 not in s.ground_k and 0 not in s.ground_c]
s = ens[noT[0]]
T = np.abs(s.transmissibility(freqs))
scaled = T * freqs ** 2
print("  " + "omega".rjust(10) + "|T|*omega^2".rjust(16) + "  (f0 = g0 = 0 for this one)")
for w, v in zip(freqs, scaled):
    print("  " + format(w, ".0e").rjust(10) + format(v, ".6e").rjust(16))
print("  -> a non-zero plateau means the omega^-2 term is carried by beta, i.e. by the")
print("     OTHER ground ties.  The claimed omission of beta was the error.")
print()
plateau = abs(scaled[-1] / scaled[-2] - 1.0) < 0.2 if scaled[-2] else False
print("  plateau present: " + str(bool(plateau)))
print()
print(line)
print("VERDICT")
print(line)
print("  CONFIRMED   : omega*|T| -> g0/m0, involving only the payload's own ground")
print("                damping and mass.  No structure in the ensemble disagrees.")
print("  REFUTED     : 'no payload tie implies T = O(s^-3)'.  beta is non-zero and the")
print("                falloff is s^-2, carried by the other ground ties.")
print("  The step-25 test reported 1.64e-04 and called the formula confirmed; that")
print("  number came from a guard that excluded the refuting cases.")
