"""Step 71 - ground truth for a witness-audit task.

Finding 043's agent rejected a counterexample I offered and was right. Finding 044 fixed the
model and reproduced its hand-computed floor exactly. What was NOT captured is HOW it reached
the objection, because the reasoning was printed as a length and discarded.

Re-running the multi-turn derivation would cost three calls and would not isolate the
capability. This builds a cheaper and sharper task instead: present several claimed witnesses,
some true and some false, and ask which are valid. A model that calls every witness invalid is
not auditing, it is disagreeing, and the mix is what separates the two.

This computes the ground truth for every candidate witness with the corrected model.
"""
import _bootstrap  # noqa: F401
import json
import pathlib

from ecdr.heat import Stream, network_lp, problem_table

STS = [Stream("H1", 150.0, 60.0, 2.0), Stream("H2", 90.0, 60.0, 8.0),
       Stream("C1", 20.0, 125.0, 2.5), Stream("C2", 100.0, 150.0, 3.0)]
DT = 10.0
QMIN = problem_table(STS, DT)["Q_H_min"]
QSTAR = 142.5

WITNESSES = [
    ("W1", {(0, 2), (1, 2)}),          # H1-C1, H2-C1   : C2 untouched
    ("W2", {(0, 2), (0, 3), (1, 2)}),  # H1-C1, H1-C2, H2-C1
    ("W3", {(0, 3), (1, 3)}),          # H1-C2, H2-C2   : C1 untouched
    ("W4", {(0, 2), (0, 3), (1, 2), (1, 3)}),   # all four matches
]

print("=" * 88)
print("GROUND TRUTH for the candidate witnesses (corrected model)")
print("=" * 88)
print("  Q_H_min (all matches allowed) = " + format(QMIN, ".6f") + "   requirement Q* = " + str(QSTAR))
print()
print("  " + "id".rjust(4) + "matches".rjust(26) + "true Q_H".rjust(13)
      + "cold streams untouched".rjust(24) + "  floor from duty".rjust(17))
out = []
for wid, ms in WITNESSES:
    r = network_lp(STS, DT, allowed=ms)
    touched_c = {j for (_, j) in ms}
    untouched = [j for j in (2, 3) if j not in touched_c]
    floor = sum(STS[j].cp * abs(STS[j].t_in - STS[j].t_out) for j in untouched)
    out.append({"id": wid, "matches": sorted([list(m) for m in ms]),
                "true_Q_H": r["Q_H"], "qstar": QSTAR,
                "meets_requirement": bool(r["Q_H"] <= QSTAR + 1e-9),
                "untouched_cold": [STS[j].name for j in untouched],
                "duty_floor": float(floor)})
    names = ", ".join(STS[i].name + "-" + STS[j].name for (i, j) in sorted(ms))
    print("  " + wid.rjust(4) + names.rjust(26) + format(r["Q_H"], ".6f").rjust(13)
          + (", ".join(STS[j].name for j in untouched) or "-").rjust(24)
          + format(floor, ".6f").rjust(17))

print()
print("=" * 88)
print("which witnesses genuinely refute a claim of Q_H <= " + str(QSTAR) + " ?")
print("=" * 88)
for w in out:
    print("  " + w["id"] + "  true Q_H = " + format(w["true_Q_H"], ".4f")
          + "   meets the requirement: " + str(w["meets_requirement"])
          + ("   <-- a VALID counterexample" if w["meets_requirement"] else ""))

path = pathlib.Path(__file__).resolve().parents[1] / "runs" / "witness_truth.json"
path.parent.mkdir(exist_ok=True)
path.write_text(json.dumps(out, indent=1), encoding="utf-8")
print()
print("wrote runs/witness_truth.json")
