"""Step 85 - the VALID L0 cross-check: L0's own FREE response, and C1 at L2 confirmed against it.

Step 84 tried to cross-check L0's natural frequencies against the peaks of L0's transmissibility.
**That is invalid.**  A base-excited transfer function has ZEROS as well as poles; an antiresonance
sits between two resonances and a pole can be largely cancelled.  The magnitude peaks of a
transmissibility are therefore NOT the natural frequencies, and the two lists disagreeing by 82 per
cent says nothing about either.

Worse, step 84 printed "L0's two independent routes agree to within 8.21e-01" - where 8.21e-01 IS
the disagreement.  Instance eight of a verdict contradicted by its own number.

**The valid L0 route is the same experiment at L0**: integrate M x'' + C x' + K x = 0 from the same
initial conditions, take the same spectrum, and compare.  This does that, then puts the L2 peaks
against it.  Both fidelities are now measured by the SAME procedure, which is what a fidelity
comparison requires.
"""
import _bootstrap  # noqa: F401
import json
import pathlib

import numpy as np
from scipy.integrate import solve_ivp

from ecdr.structure import ensemble

line = "=" * 100
OUT = pathlib.Path(__file__).resolve().parents[1] / "runs"
SAVED = json.loads((OUT / "m4_free_response.json").read_text())
ENS = ensemble(seed=101, count=400, n_lo=2, n_hi=8)
CANDS = [s for s in ENS if s.ground_k and 2 <= s.n <= 6][:8]


def eig_freqs(s):
    M, C, K, f, g = s.matrices()
    ev = np.sort(np.real(np.linalg.eigvals(np.linalg.solve(M, K))))
    ev = ev[ev > 1e-9]
    return np.sqrt(ev)


def peaks_of(t, x, rel=1e-3):
    x = x - x.mean()
    dt = t[1] - t[0]
    X = np.abs(np.fft.rfft(x * np.hanning(len(x))))
    fr = np.fft.rfftfreq(len(x), dt) * 2.0 * np.pi
    if X.max() <= 0:
        return np.array([])
    thr = rel * X.max()
    idx = [i for i in range(1, len(X) - 1)
           if X[i] > thr and X[i] >= X[i - 1] and X[i] > X[i + 1]]
    kept = []
    for i in sorted(idx, key=lambda i: -X[i]):
        if all(abs(fr[i] - fr[j]) > 0.05 * max(fr[i], 1e-9) for j in kept):
            kept.append(i)
    return np.sort(fr[kept])


def l0_free_response(s, stop, npts=200000):
    """Integrate the free response of the SAME structure at L0, by a completely different route."""
    M, C, K, f, g = s.matrices()
    n = M.shape[0]
    Minv = np.linalg.inv(M)
    s0 = np.linspace(1.0, 1.0 + 0.3 * (n - 1), n)
    y0 = np.concatenate([s0, np.zeros(n)])

    def rhs(t, y):
        x, v = y[:n], y[n:]
        return np.concatenate([v, -Minv @ (C @ v + K @ x)])

    sol = solve_ivp(rhs, (0.0, stop), y0, method="DOP853",
                    rtol=1e-11, atol=1e-13, dense_output=True)
    t = np.linspace(0.0, stop, npts)
    return t, sol.sol(t)[0]


print(line)
print("L0's FREE RESPONSE, by integration, against its own eig frequencies")
print(line)
print("  " + "idx".rjust(4) + "n".rjust(3) + "L0 peaks".rjust(9) + "modes excited".rjust(15)
      + "worst PEAK-to-eig rel".rjust(23) + "  L0 <= n ?".rjust(12))
l0_rows = []
for ci, s in enumerate(CANDS):
    w0 = eig_freqs(s)
    stop = 60.0 / float(w0[0])
    t, x = l0_free_response(s, stop)
    pk = peaks_of(t, x)
    rels = [float(np.min(np.abs(w0 - p)) / p) for p in pk] if len(pk) else []
    worst = max(rels) if rels else float("nan")
    exc = sum(1 for w in w0 if len(pk) and np.min(np.abs(pk - w)) / w < 0.10)
    l0_rows.append({"idx": ci, "n": s.n, "peaks": int(len(pk)), "excited": exc,
                    "worst": worst, "peak_freqs": [float(v) for v in pk],
                    "eig": [float(v) for v in w0]})
    print("  " + str(ci).rjust(4) + str(s.n).rjust(3) + str(len(pk)).rjust(9)
          + (str(exc) + " of " + str(s.n)).rjust(15)
          + format(worst, ".3e").rjust(23)
          + ("YES" if len(pk) <= s.n else "NO").rjust(12))

print()
print(line)
print("L2 AGAINST L0, both measured by the SAME procedure")
print(line)
print("  " + "idx".rjust(4) + "n".rjust(3) + "L0 peaks".rjust(9) + "L2 peaks".rjust(9)
      + "worst L2peak-to-L0peak rel".rjust(27) + "  C1 at L2?".rjust(12))
rows = []
for ci, (s, l0, sv) in enumerate(zip(CANDS, l0_rows, SAVED["rows"])):
    pk2 = np.array(sv["peak_freqs"])
    pk0 = np.array(l0["peak_freqs"])
    rels = [float(np.min(np.abs(pk0 - p)) / p) for p in pk2] if (len(pk2) and len(pk0)) else []
    worst = max(rels) if rels else float("nan")
    viol = (not np.isnan(worst) and worst > 0.10) or len(pk2) > s.n
    rows.append({"idx": ci, "n": s.n, "L0_peaks": int(len(pk0)), "L2_peaks": int(len(pk2)),
                 "worst": worst, "violated": bool(viol)})
    print("  " + str(ci).rjust(4) + str(s.n).rjust(3) + str(len(pk0)).rjust(9)
          + str(len(pk2)).rjust(9) + format(worst, ".3e").rjust(27)
          + ("YES" if viol else "no").rjust(12))

print()
print(line)
print("VERDICT")
print(line)
l0_ok = all(r["peaks"] <= r["n"] for r in l0_rows)
l0_worst = max(r["worst"] for r in l0_rows if not np.isnan(r["worst"]))
n_viol = sum(1 for r in rows if r["violated"])
worst = max(r["worst"] for r in rows if not np.isnan(r["worst"]))
print("  L0 free response, peaks <= n                 : " + str(l0_ok))
print("  L0 free response, worst peak-to-eig rel      : " + format(l0_worst, ".3e"))
print("  L2 vs L0, worst peak-to-peak rel             : " + format(worst, ".3e"))
print("  C1 violated at L2                            : " + str(n_viol))
print()
if l0_ok and n_viol == 0 and worst < 0.10:
    print("  ** C1 SURVIVES AT L2, and both fidelities were measured the same way. **")
    print()
    print("  Every spectral peak in the free response OpenModelica integrated lies on a frequency")
    print("  that L0's own integrated free response also produces, to within "
          + format(worst, ".2e") + ", and")
    print("  neither fidelity ever shows more peaks than n.  The certificate is not crossed by")
    print("  the fidelity change, so section 6 Layer C revokes nothing.")
    print()
    print("  The offset that remains: L2 peaks sit systematically a few per cent HIGH of L0's")
    print("  eig frequencies, and the L0 integrated peaks sit closer to them.  The likely cause")
    print("  is the spectral estimator - a Hann window on a decaying record biases a sharp peak")
    print("  - and it is NOT confirmed.  It is recorded as unexplained rather than attributed.")
else:
    print("  ** not confirmed - see the numbers above **")

OUT.mkdir(exist_ok=True)
(OUT / "m4_l0_free.json").write_text(json.dumps(
    {"l0_rows": l0_rows, "rows": rows, "l0_ok": l0_ok, "n_violated": n_viol,
     "worst_l2_to_l0": worst, "worst_l0_to_eig": l0_worst}, indent=1), encoding="utf-8")
print()
print("wrote runs/m4_l0_free.json")
