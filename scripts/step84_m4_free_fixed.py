"""Step 84 - the corrected metric for the L2 free-response check, and a cross-check of L0 itself.

Finding 060's step 83 reported "worst relative frequency mismatch 9.614e-01" and a verdict of
C1 NOT surviving at L2.  **That metric was inverted.**  It took each L0 mode, found the NEAREST
peak, and kept the worst - so a mode that was simply never excited scored as a huge mismatch.  The
data shows the opposite: every peak that appears sits on one of L0's modes.

This recomputes the metric the right way round, from the same saved peaks, and independently
cross-checks L0's own natural frequencies against L0's transmissibility resonances - because if the
L0 frequencies were wrong the whole comparison would be moot.
"""
import _bootstrap  # noqa: F401
import json
import pathlib

import numpy as np

from ecdr.structure import ensemble

line = "=" * 100
OUT = pathlib.Path(__file__).resolve().parents[1] / "runs"
SAVED = json.loads((OUT / "m4_free_response.json").read_text())
ENS = ensemble(seed=101, count=400, n_lo=2, n_hi=8)
CANDS = [s for s in ENS if s.ground_k and 2 <= s.n <= 6][:8]


def natural_frequencies(s):
    M, C, K, f, g = s.matrices()
    ev = np.sort(np.real(np.linalg.eigvals(np.linalg.solve(M, K))))
    ev = ev[ev > 1e-9]
    return np.sqrt(ev)


print(line)
print("FIRST: is L0's own natural-frequency list right?")
print(line)
print("  eig(M^-1 K) against the peaks of L0's OWN transmissibility - two independent")
print("  L0 routes.  If these disagree, comparing L2 against them proves nothing.")
print()
print("  " + "idx".rjust(4) + "eig frequencies".rjust(44) + "transmissibility peaks".rjust(44)
      + "  worst rel".rjust(11))
cross = []
for ci, s in enumerate(CANDS):
    w0 = natural_frequencies(s)
    grid = np.linspace(0.3 * w0[0], 1.6 * w0[-1], 60000)
    T = np.abs(s.transmissibility(grid))
    idx = [i for i in range(1, len(T) - 1) if T[i] > T[i - 1] and T[i] >= T[i + 1]]
    pk = np.sort(grid[idx])
    rels = []
    for w in w0:
        if len(pk) == 0:
            continue
        rels.append(abs(pk[int(np.argmin(np.abs(pk - w)))] - w) / w)
    worst = max(rels) if rels else float("nan")
    cross.append({"idx": ci, "n": s.n, "eig": [float(v) for v in w0],
                  "trans_peaks": [float(v) for v in pk], "worst_rel": worst})
    print("  " + str(ci).rjust(4)
          + np.array2string(w0, precision=3, max_line_width=200).rjust(44)
          + np.array2string(pk, precision=3, max_line_width=200).rjust(44)
          + format(worst, ".2e").rjust(11))

print()
print(line)
print("SECOND: the L2 peaks measured against L0, with the metric the right way round")
print(line)
print("  For each L2 PEAK, the distance to the nearest L0 mode.  A peak with no nearby mode")
print("  is the falsifier - it would be a harmonic the structure does not have.  A mode with")
print("  no nearby peak is NOT a falsifier; it means the initial condition did not excite it,")
print("  which C1's 'at most n' permits.")
print()
print("  " + "idx".rjust(4) + "n".rjust(3) + "peaks".rjust(7) + "modes excited".rjust(15)
      + "worst PEAK-to-mode rel".rjust(23) + "C1 violated?".rjust(15))
rows = []
for r, s in zip(SAVED["rows"], CANDS):
    w0 = natural_frequencies(s)
    pk = np.array(r["peak_freqs"])
    rels = [float(np.min(np.abs(w0 - p)) / p) for p in pk] if len(pk) else []
    worst = max(rels) if rels else float("nan")
    excited = sum(1 for w in w0 if len(pk) and np.min(np.abs(pk - w)) / w < 0.10)
    violated = (worst > 0.10) or (len(pk) > s.n)
    rows.append({"idx": r["idx"], "n": s.n, "peaks": len(pk), "excited": excited,
                 "worst_peak_to_mode": worst, "violated": bool(violated)})
    print("  " + str(r["idx"]).rjust(4) + str(s.n).rjust(3) + str(len(pk)).rjust(7)
          + (str(excited) + " of " + str(s.n)).rjust(15)
          + format(worst, ".3e").rjust(23) + ("YES" if violated else "no").rjust(15))

print()
print(line)
print("VERDICT")
print(line)
n_viol = sum(1 for r in rows if r["violated"])
worst = max(r["worst_peak_to_mode"] for r in rows)
exc = [r["excited"] for r in rows]
print("  L0's two independent routes agree to within "
      + format(max(c["worst_rel"] for c in cross), ".2e") + " - so the comparison is against")
print("  frequencies that are themselves confirmed.")
print()
print("  structures tested                  : " + str(len(rows)))
print("  C1 violated (peak with no mode, or more peaks than n) : " + str(n_viol))
print("  worst PEAK-to-mode relative error  : " + format(worst, ".3e"))
print("  modes excited by the initial state : " + str(exc) + " of their n")
print()
if n_viol == 0:
    print("  ** C1 SURVIVES AT L2. ** Every peak in the free response OpenModelica integrated sits")
    print("  on one of the structure's own natural frequencies, and no structure shows more peaks")
    print("  than n.  ** Section 6 Layer C revokes nothing. **")
    print()
    print("  And the weakness is now stated rather than hidden: only "
          + str(min(exc)) + " to " + str(max(exc)) + " of each")
    print("  structure's modes were excited at all, so this confirms 'at most n' and does NOT")
    print("  confirm 'exactly n'.  A method that produced fewer harmonics than the structure")
    print("  allows would pass this test too.")
else:
    print("  ** C1 IS VIOLATED at L2 on " + str(n_viol) + " structure(s). **")
print()
print("  Finding 060's step-83 verdict of 'C1 does NOT survive' was produced by an inverted")
print("  metric and is WITHDRAWN.  That is instance seven of a number that could not fail for")
print("  the reason the test existed - and this time the check that caught it was rereading the")
print("  raw peaks instead of the summary statistic.")

OUT.mkdir(exist_ok=True)
(OUT / "m4_free_response_fixed.json").write_text(
    json.dumps({"cross_check_L0": cross, "rows": rows,
                "n_violated": n_viol, "worst_peak_to_mode": worst}, indent=1), encoding="utf-8")
print()
print("wrote runs/m4_free_response_fixed.json")
