"""Step 59 - the Modelica emitter on arbitrary networks from ecdr.structure.

Finding 030 verified a hand-written single-degree-of-freedom model.  This drives the same
check from the STRUCTURE REPRESENTATION: a random network from the ensemble is emitted as
Modelica, simulated in the pinned container, and compared against the L0 frequency-domain
transmissibility.  If the representation cannot be emitted, L2 is not independent - the risk
recorded in Finding 009 and repeated ever since.
"""
import _bootstrap  # noqa: F401
import json
import pathlib

import numpy as np

from ecdr.l2.modelica import IMAGE, emit_model, emit_mos, simulate, steady_amplitude
from ecdr.structure import ensemble

line = "=" * 94
print(line)
print("MODELICA EMITTER on arbitrary structures")
print(line)
print("  image : " + IMAGE)

ens = ensemble(seed=5, count=40, n_lo=2, n_hi=6)
picked = [ens[0], ens[1], ens[2], ens[5]]

rows = []
for idx, s in enumerate(picked):
    M, C, K, f, g = s.matrices()
    ev = np.sort(np.linalg.eigvals(np.diag(1.0 / np.diag(M)) @ K).real)
    w1 = float(np.sqrt(max(ev[0], 1e-12)))
    for w in (0.6 * w1, 2.5 * w1):
        ref = float(np.abs(s.transmissibility(np.array([w])))[0])
        name = "NetE" + str(idx) + "W" + ("a" if w < w1 else "b")
        model = emit_model(s, w, name=name, periods=40.0)
        stop = 40.0 * 2.0 * np.pi / w
        res = simulate(model, emit_mos(name, stop, intervals=4000), name=name)
        if not res["ok"]:
            print("  structure " + str(idx) + " omega " + format(w, ".4g")
                  + " : SIMULATION FAILED")
            print("    " + res["log"][-800:].replace("\n", "\n    "))
            continue
        amp = steady_amplitude(res["t"], res["x"], w, periods_kept=3.0)
        rel = abs(amp - ref) / max(abs(ref), 1e-12)
        rows.append({"i": idx, "n": s.n, "edges": len(s.springs),
                     "ground": len(s.ground_k), "omega": float(w), "L0": ref,
                     "modelica": amp, "rel": float(rel)})
        print("  structure " + str(idx) + "  n=" + str(s.n)
              + "  edges=" + str(len(s.springs)) + "  ground=" + str(len(s.ground_k))
              + "  omega=" + format(w, ".5g")
              + "   L0 " + format(ref, ".8e")
              + "   Modelica " + format(amp, ".8e")
              + "   rel " + format(rel, ".2e"))

print()
print(line)
print("VERDICT")
print(line)
if rows:
    rel = np.array([r["rel"] for r in rows])
    print("  comparisons        : " + str(len(rows)))
    print("  median relative    : " + format(float(np.median(rel)), ".3e"))
    print("  worst relative     : " + format(float(rel.max()), ".3e"))
    print("  within 1e-4        : " + str(int((rel < 1e-4).sum())) + " of " + str(len(rel)))
    print()
    if rel.max() < 1e-3:
        print("  The structure representation SURVIVES the Modelica boundary, and arbitrary")
        print("  networks reproduce the L0 transmissibility through an equation-free model.")
        print("  Finding 009's risk 4 - that the representation might not be emittable, which")
        print("  would leave L2 a second Python model - is answered.")
    else:
        print("  Some cases disagree.  Investigate before relying on the emitter.")
else:
    print("  no successful simulations")

out = pathlib.Path(__file__).resolve().parents[1] / "runs"
out.mkdir(exist_ok=True)
(out / "modelica_ensemble.json").write_text(json.dumps({"rows": rows}, indent=1), encoding="utf-8")
print()
print("wrote runs/modelica_ensemble.json")
