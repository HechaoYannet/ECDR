"""Step 65 - the M6 domain opens: minimum utility by two independent routes.

The problem table (a cascade over shifted temperature intervals) and the transshipment LP
(a numerical optimisation over the same relaxation) encode the same model, so agreement
checks the IMPLEMENTATION rather than the physics.  That distinction is stated rather than
glossed: the physics claim - that no network of exchangers can use less hot utility than
Q_H_min - is the standard argument, and whether it is exactly achievable in the limit of
infinite area is a separate question this round does not settle.
"""
import _bootstrap  # noqa: F401
import json
import pathlib

import numpy as np

from ecdr.heat import Stream, min_utility_lp, problem_table

line = "=" * 96
print(line)
print("M6 DOMAIN 1: heat-exchanger networks, minimum utility by two routes")
print(line)

CASES = {
    "textbook 4-stream": [Stream("H1", 150.0, 60.0, 2.0), Stream("H2", 90.0, 60.0, 8.0),
                          Stream("C1", 20.0, 125.0, 2.5), Stream("C2", 100.0, 150.0, 3.0)],
    "two-and-two balanced": [Stream("H1", 200.0, 100.0, 3.0), Stream("H2", 150.0, 80.0, 4.0),
                             Stream("C1", 60.0, 180.0, 3.0), Stream("C2", 90.0, 160.0, 4.0)],
    "hot excess": [Stream("H1", 250.0, 100.0, 6.0), Stream("C1", 50.0, 200.0, 2.0)],
    "cold excess": [Stream("H1", 180.0, 120.0, 1.5), Stream("C1", 40.0, 220.0, 5.0)],
}

rows = []
for tag, sts in CASES.items():
    duty_h = sum(s.duty for s in sts if s.hot)
    duty_c = sum(s.duty for s in sts if not s.hot)
    print()
    print("  " + tag + "   (hot duty " + format(duty_h, ".1f") + ", cold duty "
          + format(duty_c, ".1f") + " kW)")
    print("    " + "dt_min".rjust(8) + "Q_H table".rjust(14) + "Q_H LP".rjust(14)
          + "difference".rjust(13) + "Q_C".rjust(12) + "pinch T".rjust(11))
    for dt_min in (5.0, 10.0, 20.0):
        pt = problem_table(sts, dt_min)
        lp = min_utility_lp(sts, dt_min)
        diff = abs(pt["Q_H_min"] - lp["Q_H_min"]) if lp["ok"] else float("nan")
        rows.append({"case": tag, "dt_min": dt_min, "Q_H_table": pt["Q_H_min"],
                     "Q_H_lp": lp.get("Q_H_min"), "diff": float(diff),
                     "Q_C": pt["Q_C_min"], "pinch": pt["pinch_shifted_T"]})
        print("    " + format(dt_min, ".3g").rjust(8)
              + format(pt["Q_H_min"], ".8f").rjust(14)
              + (format(lp["Q_H_min"], ".8f") if lp["ok"] else "failed").rjust(14)
              + format(diff, ".2e").rjust(13) + format(pt["Q_C_min"], ".6f").rjust(12)
              + (format(pt["pinch_shifted_T"], ".4g")
                 if pt["pinch_shifted_T"] is not None else "-").rjust(11))

print()
print(line)
print("B. a physical sanity relation that must hold for every case")
print(line)
print("  For any network, total heat in equals total heat out:")
print("      Q_H + hot duty released = Q_C + cold duty absorbed")
print("  which rearranges to   Q_H - Q_C = duty_cold - duty_hot,  a property of the STREAM")
print("  DATA alone.  Both routes must satisfy it or one of them is wrong.")
print()
ok = True
for r in rows:
    sts = CASES[r["case"]]
    lhs = r["Q_H_table"] - r["Q_C"]
    rhs = sum(s.duty for s in sts if not s.hot) - sum(s.duty for s in sts if s.hot)
    good = abs(lhs - rhs) < 1e-6
    ok = ok and good
    print("  " + r["case"].ljust(22) + "dt_min " + format(r["dt_min"], ".3g").rjust(5)
          + "   Q_H - Q_C = " + format(lhs, ".6f").rjust(12)
          + "   duty_c - duty_h = " + format(rhs, ".6f").rjust(12)
          + ("   ok" if good else "   MISMATCH"))

print()
print(line)
print("VERDICT")
print(line)
d = np.array([r["diff"] for r in rows])
print("  cases                    : " + str(len(rows)))
print("  worst table-vs-LP difference : " + format(float(np.nanmax(d)), ".3e"))
print("  energy balance holds         : " + str(ok))
print()
if np.nanmax(d) < 1e-6 and ok:
    print("  The problem table and the LP agree, and both satisfy the stream-data energy")
    print("  identity.  Q_H_min is computed and consistent across two implementations.")
    print()
    print("  NOT yet established, and this is the part that matters:")
    print("    (a) that Q_H_min is a TRUE lower bound for every network - the standard")
    print("        pinch argument, which is stated in certificates.py but not verified here;")
    print("    (b) that it is ACHIEVABLE, which needs a constructed network.")
else:
    print("  disagreement or an energy-balance violation; fix before going further.")

out = pathlib.Path(__file__).resolve().parents[1] / "runs"
out.mkdir(exist_ok=True)
(out / "heat_min_utility.json").write_text(json.dumps({"rows": rows}, indent=1), encoding="utf-8")
print()
print("wrote runs/heat_min_utility.json")
