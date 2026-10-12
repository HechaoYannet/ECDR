"""Step 9 - build the labelled escape-task family.

For every task in the family the registry records, per mechanism class, what is
known and HOW it is known.  The distinction matters: M1 and M3 are decided by
exact procedures, M2 only ever by a witness.  A label that hides that difference
would be dishonest, so it is carried in the record.

Output: runs/task_family.json, and a printed ladder.
"""
import _bootstrap  # noqa: F401
import json
import pathlib

import numpy as np

from ecdr.bench import (MECHANISM_ORDER, default_family_spec, make_family,
                        m1_evidence, m2_scan, m3_evidence)

line = "=" * 78
F_LOWS = [20.0, 40.0, 60.0, 80.0, 100.0, 120.0, 140.0, 160.0, 180.0, 200.0, 220.0]
spec = default_family_spec()
tasks = make_family(F_LOWS, spec)

print(line)
print("Family spec: T_iso = " + format(spec.T_iso_db, "+.0f") + " dB, A_max = "
      + format(spec.A_max_db, "+.0f") + " dB, sag <= " + format(spec.delta_mm, "g")
      + " mm, actuator budget = " + format(spec.force_budget_mult, "g") + " x wn_min^2")
print("Tasks: " + ", ".join(format(f, "g") for f in F_LOWS) + " Hz band edges")
print(line)

print()
print("exact evidence for M1 and M3 ...")
m1 = {t.name: m1_evidence(t) for t in tasks}
m3 = {t.name: m3_evidence(t) for t in tasks}
print("  M1: " + str(sum(1 for v in m1.values() if v["status"] == "feasible")) + " feasible, "
      + str(sum(1 for v in m1.values() if v["status"] == "proved_infeasible")) + " proved infeasible")
print("  M3: " + str(sum(1 for v in m3.values() if v["status"] == "feasible")) + " feasible, "
      + str(sum(1 for v in m3.values() if v["status"] == "proved_infeasible")) + " proved infeasible")

print()
print("numerical evidence for M2 (one scan answers every band edge) ...")
m2 = m2_scan(tasks)

print()
print(line)
print("ESCAPE LADDER")
print(line)
hdr = "  " + "f_low".rjust(6) + " | " + "M1".ljust(17) + " | " + "M2".ljust(17) + " | " + "M3".ljust(17) + " | min solvable"
print(hdr)
print("  " + "-" * (len(hdr) - 2))
rows = []
for t in tasks:
    e1, e2, e3 = m1[t.name], m2[t.name], m3[t.name]
    by = {"M1_passive_sdof": e1, "M2_tuned_mass_damper": e2, "M3_sky_hook_active": e3}
    minimal = None
    for name in MECHANISM_ORDER:
        if by[name]["status"] == "feasible":
            minimal = name
            break
    tag = {"feasible": "FEASIBLE", "proved_infeasible": "INFEASIBLE*",
           "no_witness_found": "no witness"}[e1["status"]]
    tag2 = {"feasible": "FEASIBLE", "proved_infeasible": "INFEASIBLE*",
            "no_witness_found": "no witness"}[e2["status"]]
    tag3 = {"feasible": "FEASIBLE", "proved_infeasible": "INFEASIBLE*",
            "no_witness_found": "no witness"}[e3["status"]]
    short = minimal.split("_")[0] if minimal else "none known"
    print("  " + format(t.f_low, "6g") + " | " + tag.ljust(17) + " | " + tag2.ljust(17)
          + " | " + tag3.ljust(17) + " | " + short)
    rows.append({
        "task_id": t.name,
        "f_low_hz": t.f_low,
        "T_iso_db": spec.T_iso_db,
        "A_max_db": spec.A_max_db,
        "delta_max_mm": spec.delta_mm,
        "m1": e1, "m2": e2, "m3": e3,
        "min_solvable_mechanism": minimal,
        "m1_infeasibility_is_a_proof": e1["status"] == "proved_infeasible",
    })
print()
print("  * INFEASIBLE means proved, by an exact procedure.  M2 never reports this:")
print("    absence of a witness is recorded as no witness, never as infeasible.")

out = pathlib.Path(__file__).resolve().parents[1] / "runs"
out.mkdir(exist_ok=True)
(out / "task_family.json").write_text(json.dumps({
    "spec": {"T_iso_db": spec.T_iso_db, "A_max_db": spec.A_max_db,
             "delta_mm": spec.delta_mm, "force_budget_mult": spec.force_budget_mult},
    "mechanism_order": list(MECHANISM_ORDER),
    "tasks": rows,
}, indent=1, default=str), encoding="utf-8")
print()
print("wrote runs/task_family.json")
