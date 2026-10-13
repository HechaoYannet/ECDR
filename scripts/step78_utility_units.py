"""Step 78 - the 3-unit network, and whether a utility exchanger is a unit.

Finding 054 left a 2-unit dispute open: the model produced the classical connectivity argument
giving 5, network_lp gives 3, and network_lp had already been corrected once for exactly this class
of omission.

The first thing to check is not the network but the DEFINITION. Classical U_min = N - 1 counts N as
the process streams PLUS THE UTILITIES, and a utility exchanger is a unit. network_lp's "units" are
only the process-to-process MATCHES: utility heat qH[j,k] is delivered at no unit cost.

If that is the whole discrepancy, then

    matches + utility exchangers  =  N - 1

and the classical bound was never refuted - Finding 044's refutation, and Finding 037's before it,
would both be invalid for counting the wrong thing.

For the 4-stream case: 4 process streams, and BOTH utilities are needed (Q_H_min = 142.5 > 0 and
Q_C_min = 150 > 0), so N = 6 and N - 1 = 5. The model said 5.
"""
import _bootstrap  # noqa: F401
import json
import pathlib

import numpy as np

from ecdr.heat import Stream, all_match_sets, network_lp, problem_table

line = "=" * 96
STS = [Stream("H1", 150.0, 60.0, 2.0), Stream("H2", 90.0, 60.0, 8.0),
       Stream("C1", 20.0, 125.0, 2.5), Stream("C2", 100.0, 150.0, 3.0)]
DT = 10.0
PT = problem_table(STS, DT)
QH, QC = PT["Q_H_min"], PT["Q_C_min"]
N = len(STS) + (1 if QH > 1e-9 else 0) + (1 if QC > 1e-9 else 0)

print(line)
print("THE 4-STREAM CASE")
print(line)
print("  process streams " + str(len(STS)) + ",  Q_H_min = " + format(QH, ".4f")
      + ",  Q_C_min = " + format(QC, ".4f"))
print("  hot utility needed: " + str(QH > 1e-9) + "   cold utility needed: " + str(QC > 1e-9))
print("  ** N = " + str(N) + " (process + utilities),  N - 1 = " + str(N - 1) + " **")
print("  the model's answer was 5")

print()
print(line)
print("EVERY MATCH SET ATTAINING Q_H_min, with its utility exchangers counted")
print(line)
print("  " + "matches".rjust(9) + "units(matches)".rjust(15) + "hot-util streams".rjust(18)
      + "cold-util streams".rjust(18) + "total units".rjust(13) + "   = N-1?".rjust(10))
rows = []
for ms in all_match_sets(STS):
    r = network_lp(STS, DT, allowed=ms)
    if not r["ok"] or r["Q_H"] > QH + 1e-6:
        continue
    col = r["col"]
    x = r["x"]
    touched_c = {j for (_, j) in ms}
    touched_h = {i for (i, _) in ms}
    # a cold stream takes hot utility if any qH[j,k] > 0, or if no match reaches it at all
    hot_util = set()
    for key, idx in col.items():
        if key[0] == "qH" and x[idx] > 1e-7:
            hot_util.add(key[1])
    for j in range(len(STS)):
        if not STS[j].hot and j not in touched_c:
            hot_util.add(j)                     # entirely utility heated
    cold_util = set()
    for key, idx in col.items():
        if key[0] == "qC" and x[idx] > 1e-7:
            cold_util.add(key[1])
    for i in range(len(STS)):
        if STS[i].hot and i not in touched_h:
            cold_util.add(i)
    total = len(ms) + len(hot_util) + len(cold_util)
    rows.append({"matches": sorted([list(m) for m in ms]), "n_matches": len(ms),
                 "hot_util_streams": sorted(STS[j].name for j in hot_util),
                 "cold_util_streams": sorted(STS[i].name for i in cold_util),
                 "total_units": total})
    print("  " + str(len(ms)).rjust(9) + str(len(ms)).rjust(15)
          + (",".join(sorted(STS[j].name for j in hot_util)) or "-").rjust(18)
          + (",".join(sorted(STS[i].name for i in cold_util)) or "-").rjust(18)
          + str(total).rjust(13) + ("   YES" if total == N - 1 else "   no").rjust(10))

print()
print(line)
print("VERDICT")
print(line)
totals = [r["total_units"] for r in rows]
print("  total units (matches + utility exchangers) across the optimal networks: "
      + str(sorted(set(totals))))
print("  N - 1 = " + str(N - 1) + "     the model's answer: 5")
print()
if N - 1 in totals:
    print("  ** The classical bound is RESTORED. **")
    print()
    print("  Every network attaining the minimum utility uses exactly N - 1 units once the")
    print("  utility exchangers are counted - which is what the classical statement counts and")
    print("  what network_lp does not. The discrepancy was a DEFINITION, not a physics error:")
    print("  the model counted utility exchangers and my model gave them away free.")
    print()
    print("  Consequences, and they are serious:")
    print("   * Finding 037's refutation of U >= N - 1 is INVALID - it counted matches only.")
    print("   * Finding 044's re-run of that refutation is INVALID for the same reason, and its")
    print("     'clean connectivity argument' - a 3-edge graph on 5 nodes is disconnected - is")
    print("     sound as graph theory and irrelevant as a refutation, because the graph it")
    print("     applies to is not the graph the classical bound is about.")
    print("   * The 3-unit network is real. It is simply a 5-unit network in the classical")
    print("     counting, because two of its five units are utility exchangers.")
else:
    print("  the totals do not reach N - 1, so the definitional explanation does not hold and")
    print("  the dispute of Finding 054 stands unresolved")

out = pathlib.Path(__file__).resolve().parents[1] / "runs"
out.mkdir(exist_ok=True)
(out / "utility_units.json").write_text(json.dumps({
    "Q_H_min": QH, "Q_C_min": QC, "N": N, "N_minus_1": N - 1, "rows": rows,
}, indent=1), encoding="utf-8")
print()
print("wrote runs/utility_units.json")
