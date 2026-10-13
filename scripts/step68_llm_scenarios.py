"""Step 68 - generate random stream sets with their ground-truth minimum utility.

Finding 041's LLM proposed exactly Q_H_min twice, but on the standard textbook 4-stream
problem, which the model may have seen in training. Exactness there is consistent both with
reasoning from the stream data and with recall, and that run could not tell them apart.

This writes scenarios with randomised temperatures, heat capacity flowrates and approach
temperatures. The ground truth comes from the problem table, verified in Finding 036 against
an independent LP and against exhaustive enumeration of every network. The values are written
to a file the orchestrator reads; the model never sees them.
"""
import _bootstrap  # noqa: F401
import json
import pathlib

import numpy as np

from ecdr.heat import Stream, problem_table

rng = np.random.default_rng(20260101)
out = []
tries = 0
while len(out) < 6 and tries < 4000:
    tries += 1
    nh = int(rng.integers(2, 4))
    nc = int(rng.integers(2, 4))
    streams = []
    for i in range(nh):
        hi = float(rng.integers(130, 260))
        lo = float(rng.integers(40, 100))
        if hi - lo < 30:
            continue
        streams.append(Stream("H" + str(i + 1), hi, lo, float(rng.integers(1, 9))))
    for j in range(nc):
        lo = float(rng.integers(20, 90))
        hi = float(rng.integers(110, 230))
        if hi - lo < 30:
            continue
        streams.append(Stream("C" + str(j + 1), lo, hi, float(rng.integers(1, 9))))
    if len(streams) != nh + nc:
        continue
    dt = float(rng.choice([5, 10, 15, 20]))
    qh = problem_table(streams, dt)["Q_H_min"]
    if qh < 5.0:
        continue                      # a vacuous certificate teaches nothing
    out.append({
        "id": "R" + str(len(out) + 1),
        "dt_min": dt,
        "Q_H_min": qh,
        "streams": [{"name": s.name, "t_in": s.t_in, "t_out": s.t_out, "cp": s.cp}
                    for s in streams],
    })

path = pathlib.Path(__file__).resolve().parents[1] / "runs" / "llm_scenarios.json"
path.parent.mkdir(exist_ok=True)
path.write_text(json.dumps(out, indent=1), encoding="utf-8")

print("=" * 88)
print("RANDOM SCENARIOS with ground truth (the model will not see the last column)")
print("=" * 88)
print("  " + "id".rjust(4) + "dt_min".rjust(8) + "streams".rjust(9)
      + "hot duty".rjust(11) + "cold duty".rjust(11) + "Q_H_min".rjust(12))
for r in out:
    hd = sum(s["cp"] * abs(s["t_in"] - s["t_out"]) for s in r["streams"] if s["t_in"] > s["t_out"])
    cd = sum(s["cp"] * abs(s["t_in"] - s["t_out"]) for s in r["streams"] if s["t_in"] < s["t_out"])
    print("  " + r["id"].rjust(4) + format(r["dt_min"], ".0f").rjust(8)
          + str(len(r["streams"])).rjust(9) + format(hd, ".1f").rjust(11)
          + format(cd, ".1f").rjust(11) + format(r["Q_H_min"], ".4f").rjust(12))
print()
print("  attempts to draw 6 non-vacuous cases: " + str(tries))
print("  wrote runs/llm_scenarios.json")
