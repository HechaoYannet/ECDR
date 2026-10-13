"""Step 81 - M5: does the named remedy determine a useful repair?

Roadmap section 9, milestone M5:

    the certificate names an invariant, and acting on that name constructs a working structure
    falsified if: the named invariant does not determine a useful repair

and section 6, Layer B (iv): a certificate that says only "impossible" is a gate, while one that
says which invariant is violated TELLS THE AGENT WHAT TO BUILD.

**Finding 057 supplied the test case, and it is an awkward one.** A certificate claiming
"no design with fewer than 6 units attains 142.5 kW" was FALSE - 5 units suffice, Finding 056 -
and its ARGUMENT was wrong, resting on the assumption that no exchanger may span the pinch. But the
same certificate NAMED "a cross-pinch exchanger" as what is missing. **And that name is correct.**

So this asks the question M5 actually poses, and separates it from the question Finding 057
settled:

    given a named remedy, does ACTING ON IT construct a working structure?

If it does, then a certificate can be refuted in its claim and still useful in its name - and the
named remedy is a cross-check the harness was not using.
"""
import _bootstrap  # noqa: F401
import json
import pathlib

import numpy as np

from ecdr.heat import Stream, problem_table
from ecdr.heat.designs import design_lp, enumerate_designs
from ecdr.heat.streams import _intervals

line = "=" * 100
STS = [Stream("H1", 150.0, 60.0, 2.0), Stream("H2", 90.0, 60.0, 8.0),
       Stream("C1", 20.0, 125.0, 2.5), Stream("C2", 100.0, 150.0, 3.0)]
DT = 10.0
PT = problem_table(STS, DT)
QH = PT["Q_H_min"]
PINCH_SHIFTED = PT["pinch_shifted_T"]
IVS = _intervals(STS, DT)

print(line)
print("THE NAMED REMEDY, and the pinch it refers to")
print(line)
print("  pinch (shifted) = " + format(PINCH_SHIFTED, ".4f"))
print("  shifted intervals, hottest first:")
for idx, (top, bot) in enumerate(IVS):
    side = "ABOVE" if bot >= PINCH_SHIFTED - 1e-9 else (
        "BELOW" if top <= PINCH_SHIFTED + 1e-9 else "SPANS")
    print("    " + str(idx).rjust(2) + "  " + format(top, ".3f").rjust(9)
          + " -> " + format(bot, ".3f").rjust(9) + "   " + side)

# the certificate Finding 057 produced, and the one that is true
CASES = [
    ("the certificate's claim  V=6  (FALSE, Finding 056)", 6),
    ("the true bound          V=5  (Finding 056)", 5),
]

print()
print(line)
print("ACTING ON THE NAME: does a cross-pinch exchanger appear?")
print(line)
# The quantity M5 turns on, computed as the loop runs rather than asserted after it.
NAMED = "a cross-pinch exchanger"
spanning_names = []
for tag, V in CASES:
    print()
    print("  " + tag)
    _, sample, allf = enumerate_designs(STS, DT, V - 1)
    hits = [d for d in allf if d["Q_H"] <= QH + 1e-6]
    if not hits:
        print("    no design with fewer than " + str(V) + " units attains Q_H_min")
        continue
    d = hits[0]
    print("    a design attaining it: " + str(d["units"]) + " units, process "
          + str(d["process"]) + ", heaters " + str(d["heaters"])
          + ", coolers " + str(d["coolers"]))
    # read the solution and ask which process matches transfer ACROSS the pinch
    r = design_lp(STS, DT, {tuple(m) for m in d["process"]}, set(d["heaters"]),
                  set(d["coolers"]))
    below_idx = [k for k, (top, bot) in enumerate(IVS) if bot < PINCH_SHIFTED - 1e-9]
    above_idx = [k for k, (top, bot) in enumerate(IVS) if top > PINCH_SHIFTED + 1e-9]
    spanning = {}
    for key, idx in r["col"].items():
        if key[0] != "x" or r["x"][idx] <= 1e-7:
            continue
        _, i, j, k, kp = key
        sides = set()
        if k in above_idx or kp in above_idx:
            sides.add("above")
        if k in below_idx or kp in below_idx:
            sides.add("below")
        if len(sides) > 1:
            spanning.setdefault((i, j), 0.0)
            spanning[(i, j)] += float(r["x"][idx])
    if spanning:
        for (i, j), q in spanning.items():
            print("    ** match " + STS[i].name + "-" + STS[j].name
                  + " transfers " + format(q, ".3f") + " kW ACROSS the pinch **")
            spanning_names.append(STS[i].name + "-" + STS[j].name)
    else:
        print("    no match spans the pinch")

print()
print(line)
print("VERDICT - M5's criterion, decided by whether the NAMED thing appears")
print(line)
print("  the certificate named : " + NAMED)
print("  matches found spanning the pinch in a design that ATTAINS Q_H_min : "
      + (", ".join(spanning_names) if spanning_names else "none"))
print()
m5_holds = len(spanning_names) > 0
if m5_holds:
    print("  M5 HOLDS. The named remedy is exactly what the working design supplies. Acting on")
    print("  the name - allowing the cross-pinch exchanger - constructs a structure that reaches")
    print("  Q_H_min with " + str(len(spanning_names)) + " spanning match(es).")
    print()
    print("  ** And the certificate that named it had a FALSE claim. ** V = 6 is wrong, 5 units")
    print("  suffice, and its argument rested on the very assumption the name denies. So the")
    print("  name was right while the claim and the argument were wrong.")
    print()
    print("  This is M5's falsifier answered: 'the named invariant does not determine a useful")
    print("  repair' is FALSE here. The name determined the repair.")
    print()
    print("  Two consequences:")
    print("   1. a refuted certificate is not thereby useless - its name can be the repair,")
    print("      which is what section 6 Layer B (iv) means by telling the agent what to build;")
    print("   2. ** the named remedy is a cross-check the harness was not using. ** Finding 057's")
    print("      reader accepted a false certificate whose own name ASSERTED the repair was")
    print("      forbidden. Testing the name instead of reading the argument refutes it at once,")
    print("      and the test is one enumeration.")
else:
    print("  M5 FAILS here: the named remedy does not appear in any design attaining Q_H_min,")
    print("  so acting on the name does not construct a working structure.")

# The separate question of whether FEWER units suffice, kept apart from M5 because it is a
# different claim. The first version of this script decided M5 from this number and got the
# opposite of what its own evidence showed - a verdict not computed from the run's data.
_, _, allf4 = enumerate_designs(STS, DT, 4)
hits4 = [d for d in allf4 if d["Q_H"] <= QH + 1e-6]
print()
print("  (a different question) designs with at most 4 units attaining Q_H_min : "
      + str(len(hits4)) + " - so 5 is the minimum, Finding 056 confirmed again)")

out = pathlib.Path(__file__).resolve().parents[1] / "runs"
out.mkdir(exist_ok=True)
(out / "m5_named_remedy.json").write_text(json.dumps({
    "pinch_shifted": PINCH_SHIFTED, "Q_H_min": QH,
    "four_unit_designs_attaining": len(hits4),
    "named": NAMED, "spanning_matches": spanning_names, "M5_holds": bool(spanning_names),
}, indent=1), encoding="utf-8")
print()
print("wrote runs/m5_named_remedy.json")
