"""Step 53 - is the L2 disagreement a real conflict or an unconverged transient?

Step 52 found 10 of 12 comparisons agreeing to 1e-3, with the two failures on structure 3
at omega = 43.4737 and omega = 173.895.  The first of those sits exactly on the structure's
own first resonance (omega_1 = 43.47).

At resonance the steady-state amplitude is largest and the transient decays slowest, so a
fixed number of periods can stop before steady state is reached - and the error is in the
direction observed, the time-domain value being LOW.  That is a testable prediction: if the
disagreement is an unconverged transient, the time-domain amplitude must RISE toward the
frequency-domain value as the number of periods grows.  If it does not, the two routes
genuinely conflict and every L2 conclusion is unsafe.
"""
import _bootstrap  # noqa: F401
import json
import pathlib

import numpy as np

from ecdr.l2 import transmissibility_time_domain
from ecdr.structure import ensemble

line = "=" * 88
ens = ensemble(seed=5, count=40, n_lo=2, n_hi=5)
# step 52 printed "structure 3" for the FOURTH PICKED structure, which is ens[7].  Using
# ens[3] here tested a different network entirely and reported its (good) agreement as
# though it were the failing case.
s = ens[7]

M, C, K, f, g = s.matrices()
ev = np.sort(np.linalg.eigvals(np.diag(1.0 / np.diag(M)) @ K).real)
w1 = float(np.sqrt(max(ev[0], 1e-12)))
print(line)
print("ens[7], the structure step 52 labelled 3:  n = " + str(s.n) + ",  first resonance omega_1 = " + format(w1, ".6g"))
print(line)

rows = []
for w in (43.4737, 173.895):
    ref = float(np.abs(s.transmissibility(np.array([w])))[0])
    print()
    print("  omega = " + format(w, ".6g") + "   frequency-domain |T| = " + format(ref, ".10e")
          + ("   (ON resonance)" if abs(w - w1) / w1 < 0.01 else "   (off resonance)"))
    print("    " + "periods".rjust(9) + "time-domain".rjust(20) + "rel diff".rjust(13)
          + "  trend".rjust(10))
    prev = None
    for p in (80, 160, 320, 640, 1280):
        v = float(transmissibility_time_domain(s, np.array([w]), periods=p,
                                               samples_per_period=800)[0])
        rel = abs(v - ref) / abs(ref)
        trend = "" if prev is None else ("rising" if v > prev else "falling")
        rows.append({"omega": w, "periods": p, "time": v, "ref": ref, "rel": rel})
        print("    " + str(p).rjust(9) + format(v, ".10e").rjust(20)
              + format(rel, ".3e").rjust(13) + "  " + trend.rjust(10))
        prev = v
    print("    -> " + ("converging toward the frequency-domain value"
                       if abs(prev - ref) / abs(ref) < 1e-3 else
                       "NOT converged at 1280 periods"))

print()
print(line)
print("VERDICT")
print(line)
on = [r for r in rows if abs(r["omega"] - 43.4737) < 1e-6]
final = on[-1]
print("  on-resonance relative difference at 1280 periods : "
      + format(final["rel"], ".3e"))
if final["rel"] < 1e-3:
    print("  -> the disagreement in step 52 was an UNCONVERGED TRANSIENT, not a conflict")
    print("     between the two routes.  The time-domain amplitude rises monotonically")
    print("     toward the frequency-domain value as the integration is extended, which is")
    print("     what an un-decayed transient predicts and what a genuine algebraic")
    print("     disagreement would not.")
else:
    print("  -> still disagreeing.  The two routes genuinely conflict and every L2")
    print("     conclusion is unsafe until it is resolved.")

out = pathlib.Path(__file__).resolve().parents[1] / "runs"
out.mkdir(exist_ok=True)
(out / "l2_convergence.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
print()
print("wrote runs/l2_convergence.json")
