"""Step 60 - is the Modelica disagreement an unsettled transient?

Step 59 found structure 0 matching L0 to 5e-06 while structures 1, 2 and 3 disagreed by up
to a factor of 3.7, with the error growing as the frequency rose.

Structure 0 is the one with THREE ground ties; the others have one or two.  Fewer ground
ties means less damping and a longer settling time, and 40 excitation periods may simply not
be enough.  That predicts the error direction: an unsettled transient makes the measured
amplitude LARGER than the steady-state value, which is what was observed.

The test is the same one Finding 026 used on the Julia rung: extend the integration and see
whether the ratio converges to 1.
"""
import _bootstrap  # noqa: F401
import json
import pathlib

import numpy as np

from ecdr.l2.modelica import emit_model, emit_mos, simulate, steady_amplitude
from ecdr.structure import ensemble

line = "=" * 92
ens = ensemble(seed=5, count=40, n_lo=2, n_hi=6)
s = ens[1]
M, C, K, f, g = s.matrices()
ev = np.sort(np.linalg.eigvals(np.diag(1.0 / np.diag(M)) @ K).real)
w1 = float(np.sqrt(max(ev[0], 1e-12)))

print(line)
print("structure 1:  n = " + str(s.n) + ",  edges = " + str(len(s.springs))
      + ",  ground ties = " + str(len(s.ground_k))
      + ",  omega_1 = " + format(w1, ".5g"))
print(line)

rows = []
for w in (91.768,):
    ref = float(np.abs(s.transmissibility(np.array([w])))[0])
    print()
    print("  omega = " + format(w, ".5g") + "   L0 |T| = " + format(ref, ".8e"))
    print("    " + "periods".rjust(9) + "stop time".rjust(11) + "intervals".rjust(11)
          + "Modelica".rjust(19) + "ratio to L0".rjust(13))
    for periods in (40, 120, 360, 1080):
        name = "NetC" + str(periods)
        model = emit_model(s, w, name=name, periods=float(periods))
        stop = periods * 2.0 * np.pi / w
        intervals = 100 * periods
        res = simulate(model, emit_mos(name, stop, intervals=intervals), name=name)
        if not res["ok"]:
            print("    " + str(periods).rjust(9) + "   SIMULATION FAILED")
            continue
        amp = steady_amplitude(res["t"], res["x"], w, periods_kept=3.0)
        ratio = amp / ref
        rows.append({"omega": w, "periods": periods, "stop": stop,
                     "intervals": intervals, "modelica": float(amp),
                     "L0": ref, "ratio": float(ratio)})
        print("    " + str(periods).rjust(9) + format(stop, ".3f").rjust(11)
              + str(intervals).rjust(11) + format(amp, ".10e").rjust(19)
              + format(ratio, ".8f").rjust(13))

print()
print(line)
print("VERDICT")
print(line)
if rows:
    r = np.array([x["ratio"] for x in rows])
    print("  ratio trend : " + ", ".join(format(v, ".6f") for v in r))
    final = rows[-1]
    rel = abs(final["ratio"] - 1.0)
    print("  final relative difference at " + str(final["periods"])
          + " periods : " + format(rel, ".3e"))
    if rel < 1e-3:
        print("  -> the disagreement was an UNCONVERGED TRANSIENT.  The ratio moves toward 1")
        print("     as the integration is extended, which is what an unsettled transient")
        print("     predicts and what a genuine modelling error would not.")
    else:
        print("  -> still disagreeing.  Investigate the emitter before trusting it.")

out = pathlib.Path(__file__).resolve().parents[1] / "runs"
out.mkdir(exist_ok=True)
(out / "modelica_convergence.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
print()
print("wrote runs/modelica_convergence.json")
