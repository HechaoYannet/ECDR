"""Step 70 - validate the corrected network model in BOTH regimes.

Finding 043: network_lp carried heat through pool variables not constrained by the match set,
so it reported utilities for networks that cannot exist. It had been validated only with every
match allowed, where the defect is invisible.

A model validated in one regime and used in another is not validated. This checks the
correction in the regime the unit-count question actually uses.
"""
import _bootstrap  # noqa: F401
import json
import pathlib

from ecdr.heat import Stream, all_match_sets, network_lp, problem_table

line = "=" * 96
CASES = {
    "4-stream": [Stream("H1", 150.0, 60.0, 2.0), Stream("H2", 90.0, 60.0, 8.0),
                 Stream("C1", 20.0, 125.0, 2.5), Stream("C2", 100.0, 150.0, 3.0)],
    "2x2": [Stream("H1", 200.0, 100.0, 3.0), Stream("H2", 150.0, 80.0, 4.0),
            Stream("C1", 60.0, 180.0, 3.0), Stream("C2", 90.0, 160.0, 4.0)],
    "3x2": [Stream("H1", 220.0, 90.0, 2.0), Stream("H2", 170.0, 70.0, 3.0),
            Stream("H3", 130.0, 60.0, 4.0),
            Stream("C1", 40.0, 190.0, 2.5), Stream("C2", 80.0, 150.0, 3.5)],
}
DT = 10.0

print(line)
print("A. the regime the model WAS validated in: EVERY match allowed")
print(line)
print("  " + "case".rjust(11) + "problem table".rjust(16) + "network_lp".rjust(16)
      + "difference".rjust(13))
rows = []
for tag, sts in CASES.items():
    ref = problem_table(sts, DT)["Q_H_min"]
    got = network_lp(sts, DT)["Q_H"]
    rows.append({"case": tag, "regime": "all matches", "reference": ref, "got": got})
    print("  " + tag.rjust(11) + format(ref, ".8f").rjust(16) + format(got, ".8f").rjust(16)
          + format(abs(got - ref), ".2e").rjust(13))

print()
print(line)
print("B. the regime the unit-count question USES: matches restricted")
print(line)
sts = CASES["4-stream"]
print("  the network the agent objected to: matches H1-C1 and H2-C1, C2 untouched")
r = network_lp(sts, DT, allowed={(0, 2), (1, 2)})
print("    network_lp with those matches      : Q_H = " + format(r["Q_H"], ".6f"))
print("    C2 duty, which no unit can supply  : 150.000000")
print("    the agent's hand-computed floor    : Q_H >= 150.000000")
ok_ce = abs(r["Q_H"] - 150.0) < 1e-6
print("    corrected model agrees with the agent: " + str(ok_ce))
print()
print("  every match set of the 4-stream case, by unit count:")
print("    " + "units".rjust(6) + "networks".rjust(10) + "best Q_H".rjust(14)
      + "  attains Q_H_min".rjust(18))
best_by_u = {}
for ms in all_match_sets(sts):
    rr = network_lp(sts, DT, allowed=ms)
    if rr["ok"]:
        best_by_u.setdefault(len(ms), []).append(rr["Q_H"])
qmin = problem_table(sts, DT)["Q_H_min"]
attain = []
for u in sorted(best_by_u):
    b = min(best_by_u[u])
    a = abs(b - qmin) < 1e-6
    if a:
        attain.append(u)
    print("    " + str(u).rjust(6) + str(len(best_by_u[u])).rjust(10)
          + format(b, ".6f").rjust(14) + ("   YES" if a else "   no").rjust(18))
print()
print("    Q_H_min = " + format(qmin, ".6f") + ",  N - 1 = 4")
print("    fewest units attaining Q_H_min = " + str(min(attain) if attain else None))

print()
print(line)
print("VERDICT")
print(line)
worst = max(abs(x["got"] - x["reference"]) for x in rows)
print("  all-matches regime, worst difference     : " + format(worst, ".3e"))
print("  restricted regime, the agent's own case  : "
      + ("reproduced exactly" if ok_ce else "STILL WRONG"))
print()
if worst < 1e-6 and ok_ce:
    print("  The corrected model reproduces the problem table where it must, AND agrees with")
    print("  the agent where the old one failed. Both regimes hold.")
    print()
    print("  So Finding 036 stands - it rested on the all-matches regime, which the correction")
    print("  leaves unchanged. And the minimum-units question can now be put to a model that")
    print("  describes realisable networks.")

out = pathlib.Path(__file__).resolve().parents[1] / "runs"
out.mkdir(exist_ok=True)
(out / "network_model_validated.json").write_text(json.dumps({
    "all_matches": rows, "counterexample_Q_H": r["Q_H"], "agent_floor": 150.0,
    "best_by_units": {str(u): float(min(v)) for u, v in best_by_u.items()},
    "fewest_units_attaining": min(attain) if attain else None,
}, indent=1), encoding="utf-8")
print()
print("wrote runs/network_model_validated.json")
