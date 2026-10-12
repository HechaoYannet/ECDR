"""Step 67 - is the minimum-units bound U >= N - 1 a SOUND certificate?

The classical result for heat exchanger networks is

    U_min = N - 1

with N the number of streams including the utilities used.  It is the combinatorial analogue
of the modal-dimension certificate - a counting statement about the network graph - and it is
the obvious second certificate for this domain.

But its soundness turns on CONNECTIVITY, which is not automatic.  A connected graph on N
nodes needs at least N - 1 edges; a DISCONNECTED one does not.  Two independent exchangers
between two hot and two cold streams use 2 units where N - 1 = 3, so if a disconnected design
can still achieve the minimum utility then U >= N - 1 is not a lower bound over all networks
and cannot be used as a certificate.

That is a question about this domain's data, not about graph theory, and the enumeration of
step 66 already contains the answer.  This extracts it.
"""
import _bootstrap  # noqa: F401
import itertools
import json
import pathlib

import numpy as np

from ecdr.heat import Stream, all_match_sets, network_lp, problem_table

line = "=" * 100
print(line)
print("Is U >= N - 1 sound?  Enumerating every network with its unit count")
print(line)

CASES = {
    "4-stream": [Stream("H1", 150.0, 60.0, 2.0), Stream("H2", 90.0, 60.0, 8.0),
                 Stream("C1", 20.0, 125.0, 2.5), Stream("C2", 100.0, 150.0, 3.0)],
    "2x2": [Stream("H1", 200.0, 100.0, 3.0), Stream("H2", 150.0, 80.0, 4.0),
            Stream("C1", 60.0, 180.0, 3.0), Stream("C2", 90.0, 160.0, 4.0)],
    "3x2": [Stream("H1", 220.0, 90.0, 2.0), Stream("H2", 170.0, 70.0, 3.0),
            Stream("H3", 130.0, 60.0, 4.0),
            Stream("C1", 40.0, 190.0, 2.5), Stream("C2", 80.0, 150.0, 3.5)],
}

rows = []
for tag, sts in CASES.items():
    dt_min = 10.0
    cert = problem_table(sts, dt_min)["Q_H_min"]
    n_streams = len(sts)
    n_util = 0 if cert < 1e-9 else 1          # a hot-utility stream exists iff it is needed
    N = n_streams + n_util
    print()
    print("  " + tag + "   streams = " + str(n_streams) + ", utilities = " + str(n_util)
          + ", N = " + str(N) + ",  N - 1 = " + str(N - 1))
    print("    certificate Q_H_min = " + format(cert, ".6f"))

    table = []
    for ms in all_match_sets(sts):
        r = network_lp(sts, dt_min, allowed=ms)
        if not r["ok"]:
            continue
        table.append((len(ms), r["Q_H"], sorted([list(m) for m in ms])))
    table.sort()

    by_u = {}
    for u, q, ms in table:
        by_u.setdefault(u, []).append(q)
    print("    " + "units".rjust(6) + "networks".rjust(10) + "best Q_H".rjust(14)
          + "  attains certificate".rjust(22))
    for u in sorted(by_u):
        best = min(by_u[u])
        att = abs(best - cert) < 1e-6
        print("    " + str(u).rjust(6) + str(len(by_u[u])).rjust(10)
              + format(best, ".6f").rjust(14) + ("   YES" if att else "   no").rjust(22))

    att_u = sorted(u for u in by_u if abs(min(by_u[u]) - cert) < 1e-6)
    u_min = min(att_u) if att_u else None
    print("    fewest units among networks attaining the certificate : " + str(u_min))
    print("    is U >= N - 1 sound here?                             : "
          + (("YES" if u_min >= N - 1 else "NO - refuted by " + str(u_min)
              + " < " + str(N - 1)) if u_min is not None else "vacuous"))
    rows.append({"case": tag, "N": N, "N_minus_1": N - 1, "certificate": cert,
                 "by_units": {str(u): len(by_u[u]) for u in sorted(by_u)},
                 "best_by_units": {str(u): float(min(by_u[u])) for u in sorted(by_u)},
                 "min_units_attaining": u_min,
                 "sound": bool(u_min is not None and u_min >= N - 1)})

print()
print(line)
print("VERDICT")
print(line)
sound = [r for r in rows if r["sound"]]
print("  cases tested                    : " + str(len(rows)))
print("  U >= N - 1 holds                : " + str(len(sound)) + " of " + str(len(rows)))
for r in rows:
    print("    " + r["case"].ljust(12) + " N-1 = " + str(r["N_minus_1"]).rjust(3)
          + "   fewest units attaining = " + str(r["min_units_attaining"]).rjust(4)
          + "   " + ("sound" if r["sound"] else "REFUTED"))
print()
if len(sound) == len(rows):
    print("  U >= N - 1 survived every case, so it is a candidate certificate for this domain.")
else:
    print("  U >= N - 1 is REFUTED as a lower bound over all networks.  Networks exist that")
    print("  attain the minimum utility with fewer units than N - 1, which is possible exactly")
    print("  because such a network is DISCONNECTED - each component needs only its own")
    print("  spanning tree.  Stating it as a certificate would have been an unsound claim of")
    print("  precisely the kind this project is built to avoid.")

out = pathlib.Path(__file__).resolve().parents[1] / "runs"
out.mkdir(exist_ok=True)
(out / "heat_min_units.json").write_text(json.dumps({"rows": rows}, indent=1),
                                         encoding="utf-8")
print()
print("wrote runs/heat_min_units.json")
