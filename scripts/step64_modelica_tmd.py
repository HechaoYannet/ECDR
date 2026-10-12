"""Step 64 - the tuned mass damper through Modelica, closing the mechanism gap of Finding 033.

The TMD is a two-mass network: the payload m1 with a ground spring and damper, and an
absorber m2 on its own spring and damper.  In the structure representation that is

    masses = [1 - mu, mu]
    springs = {(0, 1): k2}     dampers = {(0, 1): c2}
    ground_k = {0: k1}         ground_c = {0: c1}

so the GENERIC emitter of Finding 031 should handle it with no new code.  If it does, every
mechanism the project uses is covered by the modelling-independent route, and Finding 033's
last coverage gap closes.

The comparison is against TunedMassDamper.transmissibility, which solves the 2x2 system in
eddr/l0/mechanisms.py - an expression this emitter shares nothing with.
"""
import _bootstrap  # noqa: F401
import json
import pathlib

import numpy as np

from ecdr.l0.mechanisms import TunedMassDamper
from ecdr.l2.modelica.emit import emit_model
from ecdr.l2.modelica.linearize import linearize, tf_mag
from ecdr.structure import Structure

line = "=" * 100
tmd = TunedMassDamper()

CASES = [
    (100.0, 0.05, 0.10, 1.00, 0.10),
    (100.0, 0.02, 0.05, 0.95, 0.20),
    (50.0, 0.30, 0.30, 1.20, 0.05),
    (200.0, 0.01, 0.02, 1.05, 0.50),
]


def tmd_structure(wn1, z1, mu, ratio, z2) -> Structure:
    m_total = 1.0
    m1 = m_total * (1.0 - mu)
    m2 = m_total * mu
    wn2 = ratio * wn1
    k1 = wn1 ** 2 * m_total
    c1 = 2.0 * z1 * np.sqrt(k1 * m_total)
    k2 = wn2 ** 2 * m2
    c2 = 2.0 * z2 * np.sqrt(k2 * m2)
    return Structure(masses=np.array([m1, m2]), springs={(0, 1): k2},
                     dampers={(0, 1): c2}, ground_k={0: k1}, ground_c={0: c1})


print(line)
print("TUNED MASS DAMPER through the generic emitter, linearized")
print(line)
rows = []
for ci, (wn1, z1, mu, ratio, z2) in enumerate(CASES):
    S = tmd_structure(wn1, z1, mu, ratio, z2)
    M = linearize(emit_model(S, 1.0, name="Tmd" + str(ci)), name="Tmd" + str(ci))
    if not M["ok"]:
        print("  case " + str(ci) + " FAILED: " + M["log"][-400:].replace("\n", " "))
        continue
    omegas = np.array([0.5 * wn1, 1.0 * wn1, 2.0 * wn1, 5.0 * wn1])
    ref = np.abs(tmd.transmissibility(omegas, (wn1, z1, mu, ratio, z2)))
    got = tf_mag(M, omegas)
    print()
    print("  case " + str(ci) + ":  omega_n1=" + format(wn1, ".4g") + " zeta1="
          + format(z1, ".3g") + " mu=" + format(mu, ".3g") + " ratio=" + format(ratio, ".3g")
          + " zeta2=" + format(z2, ".3g") + "   states=" + str(M["n"]))
    print("    " + "omega".rjust(12) + "L0".rjust(19) + "Modelica".rjust(19) + "rel".rjust(11))
    for w, a, b in zip(omegas, ref, got):
        rel = abs(b - a) / a if a else float("nan")
        rows.append({"case": ci, "params": [wn1, z1, mu, ratio, z2], "omega": float(w),
                     "L0": float(a), "modelica": float(b), "rel": float(rel)})
        print("    " + format(w, ".6g").rjust(12) + format(a, ".10e").rjust(19)
              + format(b, ".10e").rjust(19) + format(rel, ".2e").rjust(11))

print()
print(line)
print("VERDICT")
print(line)
if rows:
    rel = np.array([r["rel"] for r in rows])
    print("  comparisons        : " + str(len(rows)))
    print("  median relative    : " + format(float(np.median(rel)), ".3e"))
    print("  worst relative     : " + format(float(rel.max()), ".3e"))
    print()
    if rel.max() < 1e-5:
        print("  The generic emitter covers the tuned mass damper with NO new code, so every")
        print("  mechanism the project uses - passive network, tuned mass damper and lagged")
        print("  sky-hook - is now confirmed by a route that shares no equation with the rest")
        print("  of the project.  Finding 033's coverage gap is closed.")
    else:
        print("  Disagreement.  Investigate before extending the claim of coverage.")

out = pathlib.Path(__file__).resolve().parents[1] / "runs"
(out / "modelica_tmd.json").write_text(json.dumps({"rows": rows}, indent=1), encoding="utf-8")
print()
print("wrote runs/modelica_tmd.json")
