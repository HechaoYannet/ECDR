"""Step 83 - M4's soundness half: C1 checked against a FREE response at L2.

Finding 060 recorded that two attempts to re-check C1 at L2 were invalid.  The first used a
FORCED-response magnitude to test a free-response claim; the second counted the poles of a
base-excited model and found n + 1 oscillatory pairs, because the excitation contributes a state.

**Both failures had the same cause: no model here had a free response.**  This one does.  The
emitter's new emit_free_model has no input at all - the ground is a Fixed component and the motion
comes from nonzero initial conditions - so what OpenModelica integrates is a genuine free response.

C1 says: an n-degree-of-freedom structure's free response is a sum of at most n harmonics.

The test has to be able to FAIL, which neither previous attempt could.  So it checks two things
that a wrong C1 would break:
  * the number of distinct spectral peaks in the L2 free response is at most n;
  * and the peak FREQUENCIES match the natural frequencies computed independently in Python.
A model that produced more peaks than n, or peaks at frequencies the structure does not have,
would falsify it.
"""
import _bootstrap  # noqa: F401
import json
import pathlib

import numpy as np

from ecdr.l2.modelica.emit import emit_free_model, emit_mos
from ecdr.l2.modelica.run import simulate
from ecdr.structure import ensemble

line = "=" * 100
OUT = pathlib.Path(__file__).resolve().parents[1] / "runs"


def natural_frequencies(s):
    """L0's own modes, from the mass and stiffness matrices.  None if ungrounded."""
    M, C, K, f, g = s.matrices()
    if not s.ground_k:
        return None
    ev = np.linalg.eigvals(np.linalg.solve(M, K))
    ev = np.sort(np.real(ev))
    ev = ev[ev > 1e-9]
    return np.sqrt(ev)


def spectral_peaks(t, x, rel=1e-3):
    """Frequencies of the local maxima of |X(f)| above rel times the largest."""
    x = x - x.mean()
    dt = t[1] - t[0]
    win = np.hanning(len(x))
    X = np.abs(np.fft.rfft(x * win))
    fr = np.fft.rfftfreq(len(x), dt) * 2.0 * np.pi          # rad/s
    if X.max() <= 0:
        return np.array([])
    thr = rel * X.max()
    idx = [i for i in range(1, len(X) - 1)
           if X[i] > thr and X[i] >= X[i - 1] and X[i] > X[i + 1]]
    # merge peaks closer than 5 per cent, keeping the taller
    kept = []
    for i in sorted(idx, key=lambda i: -X[i]):
        if all(abs(fr[i] - fr[j]) > 0.05 * max(fr[i], 1e-9) for j in kept):
            kept.append(i)
    return np.sort(fr[kept])


print(line)
print("C1 AT L2, ON A FREE RESPONSE")
print(line)
print("  C1: an n-degree-of-freedom structure's free response has at most n harmonics.")
print()

ens = ensemble(seed=101, count=400, n_lo=2, n_hi=8)
cands = [s for s in ens if s.ground_k and 2 <= s.n <= 6][:8]

rows = []
print("  " + "idx".rjust(4) + "n".rjust(3) + "peaks at L2".rjust(13)
      + "<= n ?".rjust(8) + "  L0 natural frequencies (rad/s)".rjust(42)
      + "   worst rel match".rjust(17))
for ci, s in enumerate(cands):
    w0 = natural_frequencies(s)
    if w0 is None or len(w0) < 2:
        continue
    name = "Free" + str(ci)
    stop = 60.0 / float(np.min(w0))          # many periods of the slowest mode
    model = emit_free_model(s, name=name)
    mos = emit_mos(name, stop, intervals=20000, tolerance=1e-10)
    r = simulate(model, mos, name=name)
    if not r["ok"]:
        print("  " + str(ci).rjust(4) + str(s.n).rjust(3) + "   SIMULATION FAILED: "
              + r["log"][-200:].replace("\n", " "))
        continue
    pk = spectral_peaks(r["t"], r["x"])
    # match each L0 mode to the nearest peak
    rels = []
    for w in w0:
        if len(pk) == 0:
            rels.append(float("inf"))
            continue
        j = int(np.argmin(np.abs(pk - w)))
        rels.append(abs(pk[j] - w) / w)
    worst = float(np.max(rels)) if rels else float("inf")
    holds = len(pk) <= s.n
    rows.append({"idx": ci, "n": s.n, "peaks": int(len(pk)),
                 "peak_freqs": [float(v) for v in pk],
                 "L0_freqs": [float(v) for v in w0], "worst_rel": worst,
                 "holds": bool(holds), "stop_time": stop})
    print("  " + str(ci).rjust(4) + str(s.n).rjust(3) + str(len(pk)).rjust(13)
          + ("YES" if holds else "NO").rjust(8) + "  "
          + np.array2string(w0, precision=4, max_line_width=200).rjust(42)
          + format(worst, ".3e").rjust(17))

print()
print(line)
print("VERDICT")
print(line)
if not rows:
    print("  no structure produced a usable free response")
else:
    holds = sum(1 for r in rows if r["holds"])
    worst = max(r["worst_rel"] for r in rows)
    print("  structures tested            : " + str(len(rows)))
    print("  peaks <= n (C1 holds at L2)  : " + str(holds) + " of " + str(len(rows)))
    print("  worst relative frequency mismatch against L0's own modes : "
          + format(worst, ".3e"))
    print()
    if holds == len(rows) and worst < 0.05:
        print("  ** C1 HOLDS at L2, checked on a free response. ** The number of harmonics in")
        print("  the response OpenModelica integrated never exceeds n, and the frequencies are")
        print("  the structure's own - computed independently in Python from M and K.")
        print()
        print("  This is the check Finding 060 recorded as missing. The two failed attempts")
        print("  failed because no model here had a free response; this one does, and the claim")
        print("  survives the fidelity change. ** Under section 6 Layer C nothing is revoked. **")
    else:
        print("  ** C1 does NOT survive unchanged at L2. ** Either the harmonic count exceeds n")
        print("  or the frequencies are not the structure's own, and section 6 Layer C says a")
        print("  certificate crossed by a higher fidelity is REVOKED, not edited.")
        for r in rows:
            if not r["holds"]:
                print("    idx " + str(r["idx"]) + "  n=" + str(r["n"]) + " but "
                      + str(r["peaks"]) + " peaks at " + str(r["peak_freqs"]))

out = OUT
out.mkdir(exist_ok=True)
(out / "m4_free_response.json").write_text(json.dumps({"rows": rows}, indent=1), encoding="utf-8")
print()
print("wrote runs/m4_free_response.json")
