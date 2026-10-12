"""Step 57 - how many "robust" L1 designs fail once the worst case is exact?

A maximum over n_pert random perturbation directions is only a LOWER bound on the maximum
over the box.  Finding 028 established this for robust_violation on the passive SDOF and
moved the +-10 percent threshold from 239.72 Hz to 258.76 Hz.  MechanismProblemL1 and
verify_l1 had exactly the same construction, so every L1 label in the project inherits it.

Both now accept use_corners=True, which evaluates the 2^d corners of the box - exact under
monotonicity, and at most 8 points for the three-parameter lagged sky-hook.

This sweeps M1 across the six task frequencies at two perturbation radii and counts how
many designs the sampled test certifies and the corner test rejects.
"""
import _bootstrap  # noqa: F401
import json
import pathlib

import numpy as np

from ecdr.bench import default_family_spec
from ecdr.l0 import G, PassiveSDOF
from ecdr.l1 import verify_l1

line = "=" * 96
spec = default_family_spec()
F_LOWS = [150.0, 180.0, 210.0, 240.0, 280.0, 320.0]
ZONE = (172.34, 258.76)
m1 = PassiveSDOF()

# M1 design grid: wn from the sag floor upward, zeta over the useful range
wn_min = float(np.sqrt(G / 1.0e-3))
grid = [(wn, float(z)) for wn in np.linspace(wn_min, 3.0 * wn_min, 60)
        for z in np.linspace(0.3, 1.6, 40)]

print(line)
print("A. designs the SAMPLED test certifies and the CORNER test rejects")
print(line)
print("  " + "f_low".rjust(7) + "rel".rjust(6) + "L0 feas".rjust(9) + "sampled ok".rjust(12)
      + "corners ok".rjust(12) + "FALSE ROBUST".rjust(14) + "  in zone".rjust(10))
rows = []
for f in F_LOWS:
    task = spec.task(f)
    for rel in (0.06, 0.10):
        n_s = n_c = n_bad = 0
        for p in grid:
            try:
                ws = verify_l1(m1, p, task, rel=rel, n_pert=24, use_corners=False)
                wc = verify_l1(m1, p, task, rel=rel, n_pert=24, use_corners=True)
            except Exception:
                continue
            if ws["meets_isolation_target"]:
                n_s += 1
                if not wc["meets_isolation_target"]:
                    n_bad += 1
            if wc["meets_isolation_target"]:
                n_c += 1
        inzone = ZONE[0] < f < ZONE[1]
        rows.append({"f_low": f, "rel": rel, "sampled_ok": n_s, "corners_ok": n_c,
                     "false_robust": n_bad, "in_zone": bool(inzone)})
        print("  " + format(f, ".0f").rjust(7) + format(rel, ".2f").rjust(6)
              + str(n_c > 0).rjust(9) + str(n_s).rjust(12) + str(n_c).rjust(12)
              + str(n_bad).rjust(14) + "  " + str(inzone).rjust(8))

print()
print(line)
print("B. VERDICT")
print(line)
tot_bad = sum(r["false_robust"] for r in rows)
print("  total false-robust designs across the sweep : " + str(tot_bad))
bad_rows = [r for r in rows if r["false_robust"] > 0]
if bad_rows:
    print("  affected (f_low, rel) pairs                 : " + str(len(bad_rows)))
    for r in bad_rows:
        print("    f_low = " + format(r["f_low"], ".0f") + ", rel = " + format(r["rel"], ".2f")
              + " : sampled ok " + str(r["sampled_ok"]) + ", corners ok " + str(r["corners_ok"])
              + ", false robust " + str(r["false_robust"]))
    print()
    print("  -> the sampled worst case is NOT adequate for L1, and every label produced")
    print("     with it is optimistic in the same direction as Finding 028.")
else:
    print("  No design the sampled test certifies fails the corner test on this sweep.")

print()
print(line)
print("C. the corrected false-positive zone and the task stratification")
print(line)
inside = [f for f in F_LOWS if ZONE[0] < f < ZONE[1]]
print("  zone at rel = 0.10 : " + format(ZONE[0], ".2f") + " to " + format(ZONE[1], ".2f")
      + " Hz")
print("  tasks inside : " + str(inside))
print("  tasks above  : " + str([f for f in F_LOWS if f >= ZONE[1]]))
print("  tasks below  : " + str([f for f in F_LOWS if f <= ZONE[0]]))
print()
print("  step 17 stratified by 172.34 to 239.72, which placed 240 Hz ABOVE the zone.")
print("  Corrected, 240 Hz is INSIDE it.")

out = pathlib.Path(__file__).resolve().parents[1] / "runs"
out.mkdir(exist_ok=True)
(out / "l1_labels_corrected.json").write_text(json.dumps({
    "rows": rows, "total_false_robust": tot_bad, "zone": list(ZONE),
    "inside": inside,
}, indent=1), encoding="utf-8")
print()
print("wrote runs/l1_labels_corrected.json")
