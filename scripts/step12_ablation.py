"""Step 12 - the headline ablation.

Hypothesis under test (README section 8, revised in Finding 005):

    Under a FIXED mechanism inventory and a FIXED evaluation budget, an agent that
    abandons a mechanism class on a SOUND certificate escapes a provably inadequate
    design space more often, and at lower cost, than one that abandons on a
    performance score, a failure streak, or a surrogate prediction.

Design: everything is held fixed except the abandonment signal.  Two certificate
arms are reported because Finding 005 concluded the honest proposal is the hybrid:

    certificate_pure    sound pruning only, no fallback.  Included to show its cost:
                        with no certificate for the intermediate class it cannot
                        leave it.
    certificate_hybrid  hard where certified, soft elsewhere -- CORE three-tier
                        discipline, and the arm the thesis actually proposes.

Success is decided by the exact peak routine.  Cost is counted in objective
evaluations, which is the ledger the mechanisms share.
"""
import _bootstrap  # noqa: F401
import json
import pathlib
import statistics
import time

from ecdr.agent import ARM_LABELS, run_episode
from ecdr.bench import default_family_spec

ROOT = pathlib.Path(__file__).resolve().parents[1]
F_LOWS = [20.0, 40.0, 60.0, 80.0, 100.0, 120.0, 140.0, 160.0, 180.0, 200.0, 220.0]
BUDGET = 2500
SEEDS = [0, 1, 2]
ARMS = ["never", "streak", "plateau", "surrogate",
        "certificate_pure", "certificate_hybrid", "oracle"]

labels = json.loads((ROOT / "runs" / "task_family.json").read_text(encoding="utf-8"))
minimal = {row["task_id"]: row["min_solvable_mechanism"] for row in labels["tasks"]}
# the oracle knows which mechanisms CAN work, not merely which is smallest
feasibility = {}
for row in labels["tasks"]:
    feasibility[row["task_id"]] = {
        "M1_passive_sdof": row["m1"]["status"] == "feasible",
        "M2_tuned_mass_damper": row["m2"]["status"] == "feasible",
        "M3_sky_hook_active": row["m3"]["status"] == "feasible",
    }

spec = default_family_spec()
tasks = [spec.task(f) for f in F_LOWS]

line = "=" * 78
print(line)
print("HEADLINE ABLATION: fixed inventory, fixed budget, only the pruning signal varies")
print("budget = " + str(BUDGET) + " evaluations per episode, seeds = " + str(SEEDS))
print(line)

records = []
t0 = time.time()
for task in tasks:
    m = minimal.get(task.name)
    fm = feasibility.get(task.name, {})
    for arm in ARMS:
        for s in SEEDS:
            r = run_episode(task, arm, fm, budget=BUDGET, seed=s)
            r["minimal_class"] = m
            r["seed"] = s
            records.append(r)
    done = len(records)
    print("  " + task.name.ljust(22) + " done, " + str(done) + " episodes, "
          + format(time.time() - t0, ".0f") + " s")

# ---- summarise -------------------------------------------------------------
def regime(f):
    if f < 132.43:
        return "depth3"
    if f < 172.24:
        return "depth2"
    return "depth1"


print()
print(line)
print("ESCAPE RATE AND COST BY ARM  (success verified with the exact peak routine)")
print(line)
print("  " + "arm".ljust(19) + "escape".rjust(8) + "reached".rjust(9)
      + "  median WASTED".rjust(15) + "  median evals".rjust(14) + "  worst WASTED".rjust(14))
summary = {}
for arm in ARMS:
    rs = [r for r in records if r["arm"] == arm]
    succ = [r for r in rs if r["escaped"]]
    rate = len(succ) / len(rs)
    reached = sum(1 for r in rs if r["reached_feasible_mechanism"] is not None) / len(rs)
    med_s = statistics.median([r["evals_to_success"] for r in succ]) if succ else None
    med_w = statistics.median([r["wasted"] for r in rs])
    max_w = max(r["wasted"] for r in rs)
    summary[arm] = {"escape_rate": rate, "reached_feasible_rate": reached,
                    "median_wasted": med_w, "max_wasted": max_w,
                    "median_cost_success": med_s, "n": len(rs)}
    print("  " + arm.ljust(19) + format(100 * rate, "6.1f") + "%" + format(100 * reached, "8.1f") + "%"
          + format(med_w, "15.0f")
          + (format(med_s, "14.0f") if med_s else "             -")
          + format(max_w, "14.0f"))

print()
print(line)
print("STRATIFIED BY ESCAPE DEPTH")
print(line)
print("  " + "arm".ljust(19) + "depth1".rjust(9) + "depth2".rjust(9) + "depth3".rjust(9))
for arm in ARMS:
    row = []
    for reg in ("depth1", "depth2", "depth3"):
        rs = [r for r in records if r["arm"] == arm and regime(r["f_low_hz"] if "f_low_hz" in r else 0.0) == reg]
        row.append(rs)
    cells = []
    for reg in ("depth1", "depth2", "depth3"):
        rs = [r for r in records if r["arm"] == arm
              and regime(float(r["task"].split("_f")[1].split("_")[0])) == reg]
        cells.append(format(100 * sum(1 for r in rs if r["escaped"]) / len(rs), "7.0f") + "%" if rs else "      -")
    print("  " + arm.ljust(19) + "".join(c.rjust(9) for c in cells))

out = ROOT / "runs" / "ablation.json"
out.write_text(json.dumps({
    "budget": BUDGET, "seeds": SEEDS, "arms": ARMS,
    "arm_labels": ARM_LABELS, "summary": summary,
    "records": [{k: v for k, v in r.items() if k != "trace"} for r in records],
}, indent=1, default=str), encoding="utf-8")
print()
print("wrote runs/ablation.json  (" + str(len(records)) + " episodes)")
