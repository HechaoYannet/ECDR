"""Step 17 - the L1 ablation: does respecting the domain of validity pay?

At L0 the experiment was degenerate, because the certifier could decide both M1 and
M3 exactly.  L1 removes that: an L0 infeasibility proof still transfers upward, but
an L0 FEASIBILITY verdict does not.  For 172.34 < f_low < 239.72 Hz the L0
certificate is confidently wrong about M1.

So the sharp comparison is between two certificate arms that differ ONLY in whether
they respect pruning rule P7:

  certificate_naive_L1   treats "feasible at L0" as licence to keep searching
  certificate_hybrid_L1  treats it as UNKNOWN and falls back to soft guidance

A third failure mode appears here that the L0 experiment could not show: the naive
arm does not merely waste budget, it DELIVERS a design that passes every L0 check
and fails under perturbation.
"""
import _bootstrap  # noqa: F401
import json, pathlib, statistics, time
import numpy as np
from ecdr.agent.episode import MECHANISMS_L1, run_episode_l1
from ecdr.agent.search import PopulationSearch
from ecdr.bench import default_family_spec
from ecdr.l1 import MechanismProblemL1, verify_l1

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = default_family_spec()
F_LOWS = [150.0, 180.0, 210.0, 240.0, 280.0, 320.0]
tasks = [spec.task(f) for f in F_LOWS]
BUDGET = 1500
SEEDS = [0, 1, 2]
ARMS = ["never", "streak", "plateau", "surrogate",
        "certificate_naive_L1", "certificate_hybrid_L1", "oracle"]
# certificate_hybrid_L1 now falls back to Plateau, the strongest soft heuristic,
# so the comparison isolates the certificate's MARGINAL value on top of the best
# heuristic rather than the quality of an arbitrary fallback.

line = "=" * 78
print(line)
print("LABELLING: which mechanisms are actually feasible at L1?")
print(line)
labels = {}
for task in tasks:
    labels[task.name] = {}
    row = []
    for name in MECHANISMS_L1:
        mech = MECHANISMS_L1[name]()
        problem = MechanismProblemL1(task, mech, rel=0.06, n_pert=5, seed=3)
        search = PopulationSearch(problem, seed=99, popsize=24, offspring=24)
        found = False
        for _ in range(140):
            search.generation()
            if search.best_obj >= -task.T_iso:
                v = verify_l1(mech, search.best_x, task, rel=0.06)
                if v["meets_isolation_target"]:
                    found = True
                    break
        labels[task.name][name] = found
        row.append(name.split("_")[0] + ("=Y" if found else "=n"))
    print("  " + task.name.ljust(22) + " ".join(row))

print()
print(line)
print("ABLATION AT L1")
print(line)
records = []
t0 = time.time()
for task in tasks:
    fm = labels[task.name]
    for arm in ARMS:
        for s in SEEDS:
            r = run_episode_l1(task, arm, fm, budget=BUDGET, seed=s)
            r["seed"] = s
            records.append(r)
    print("  " + task.name.ljust(22) + str(len(records)) + " episodes, "
          + format(time.time() - t0, ".0f") + " s")

print()
print(line)
print("RESULTS")
print(line)
print("  " + "arm".ljust(22) + "escape".rjust(8) + "median WASTED".rjust(15) + "worst WASTED".rjust(14))
summary = {}
for arm in ARMS:
    rs = [r for r in records if r["arm"] == arm]
    rate = sum(1 for r in rs if r["escaped"]) / len(rs)
    med = statistics.median([r["wasted"] for r in rs])
    mx = max(r["wasted"] for r in rs)
    summary[arm] = {"escape_rate": rate, "median_wasted": med, "max_wasted": mx}
    print("  " + arm.ljust(22) + format(100 * rate, "6.1f") + "%"
          + format(med, "15.0f") + format(mx, "14.0f"))

print()
print(line)
print("STRATIFIED: the false-positive zone is 172.34 < f_low < 239.72 Hz")
print(line)
print("  " + "arm".ljust(22) + "below zone".rjust(12) + "IN ZONE".rjust(10) + "above zone".rjust(12))
def zone(f):
    return "below" if f < 172.34 else ("in" if f < 239.72 else "above")
for arm in ARMS:
    cells = []
    for z in ("below", "in", "above"):
        sub = [r for r in records if r["arm"] == arm
               and zone(float(r["task"].split("_f")[1].split("_")[0])) == z]
        cells.append(format(100 * sum(1 for r in sub if r["escaped"]) / len(sub), "10.0f") + "%"
                     if sub else "         -")
    print("  " + arm.ljust(22) + "".join(c.rjust(12) for c in cells))

out = ROOT / "runs" / "l1_ablation.json"
out.write_text(json.dumps({"budget": BUDGET, "seeds": SEEDS, "f_lows": F_LOWS,
                           "labels": labels, "summary": summary,
                           "records": [{k: v for k, v in r.items() if k != "trace"}
                                       for r in records]}, indent=1, default=str),
               encoding="utf-8")
print()
print("wrote runs/l1_ablation.json (" + str(len(records)) + " episodes)")
