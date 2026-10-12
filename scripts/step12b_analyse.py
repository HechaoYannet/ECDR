"""Stratified analysis of the ablation, isolating decision quality from search strength."""
import json, pathlib, statistics
ROOT = pathlib.Path(__file__).resolve().parents[1]
d = json.loads((ROOT / "runs" / "ablation.json").read_text(encoding="utf-8"))
recs = d["records"]
BUDGET = d["budget"]

def regime(task):
    f = float(task.split("_f")[1].split("_")[0])
    return "depth3" if f < 132.43 else ("depth2" if f < 172.24 else "depth1")

ARMS = ["never", "streak", "plateau", "surrogate", "certificate_pure", "certificate_hybrid", "oracle"]
print("MEDIAN WASTED BUDGET (evaluations spent on mechanisms that cannot work)")
print("  lower is better; this measures the DECISION, not the inner search")
print()
print("  " + "arm".ljust(19) + "all".rjust(8) + "depth1".rjust(9) + "depth2".rjust(9) + "depth3".rjust(9))
for arm in ARMS:
    rs = [r for r in recs if r["arm"] == arm]
    row = [statistics.median([r["wasted"] for r in rs])]
    for reg in ("depth1", "depth2", "depth3"):
        sub = [r for r in rs if regime(r["task"]) == reg]
        row.append(statistics.median([r["wasted"] for r in sub]) if sub else float("nan"))
    print("  " + arm.ljust(19) + "".join(format(v, "9.0f") for v in row))

print()
print("ESCAPE RATE (verified with the exact peak routine)")
print()
print("  " + "arm".ljust(19) + "all".rjust(8) + "depth1".rjust(9) + "depth2".rjust(9) + "depth3".rjust(9))
for arm in ARMS:
    rs = [r for r in recs if r["arm"] == arm]
    row = [100.0 * sum(1 for r in rs if r["escaped"]) / len(rs)]
    for reg in ("depth1", "depth2", "depth3"):
        sub = [r for r in rs if regime(r["task"]) == reg]
        row.append(100.0 * sum(1 for r in sub if r["escaped"]) / len(sub) if sub else float("nan"))
    print("  " + arm.ljust(19) + "".join(format(v, "8.0f") + "%" for v in row))

print()
print("CONFOUND CHECK: on depth-2 tasks the only searchable feasible class is M2.")
print("If an arm abandons M2 it lands on M3, which ALSO works and is easier to search,")
print("so a wrong abandonment is rewarded.  Evidence:")
for arm in ["oracle", "certificate_hybrid", "surrogate", "streak"]:
    sub = [r for r in recs if r["arm"] == arm and regime(r["task"]) == "depth2"]
    esc = 100.0 * sum(1 for r in sub if r["escaped"]) / len(sub) if sub else float("nan")
    used = {}
    for r in sub:
        if r["escaped"]:
            used[r["mechanism_used"]] = used.get(r["mechanism_used"], 0) + 1
    print("  " + arm.ljust(19) + "escape=" + format(esc, "5.0f") + "%   solved by: " + str(used))

print()
print("The oracle is an upper bound on decision quality, so it can never legitimately")
print("lose on escape rate.  Where it does, the loss is caused by the inner search,")
print("not by the decision: that is the confound escape rate carries here.")
