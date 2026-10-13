"""Step 72 - training observations and a held-out case for a bound WE DO NOT KNOW.

Finding 048: the heat-domain demonstrations were circular because the checker and the ground
truth were the same algorithm, so agreement between them proved nothing. The one non-circular
test available is to ask for a bound nobody has: the corrected minimum-units relation.

Finding 037 proposed U >= N - 1 and Finding 044 refuted it - the 4-stream case attains the
minimum utility with 3 units against N - 1 = 4. No replacement has been found. **We cannot
precompute an answer we do not have.**

This produces observations for the agent (stream data -> the fewest units any network attaining
the minimum utility needs) and ONE held-out case it will not see the answer to.
"""
import _bootstrap  # noqa: F401
import itertools
import json
import pathlib

import numpy as np

from ecdr.heat import Stream, all_match_sets, network_lp, problem_table

rng = np.random.default_rng(4242)


def minimum_units_attaining(streams, dt):
    """Fewest units among the networks that attain the minimum hot utility."""
    qmin = problem_table(streams, dt)["Q_H_min"]
    best = None
    for ms in all_match_sets(streams):
        r = network_lp(streams, dt, allowed=ms)
        if not r["ok"]:
            continue
        if r["Q_H"] <= qmin + 1e-6 and (best is None or len(ms) < best):
            best = len(ms)
    return qmin, best


def draw(nh, nc):
    for _ in range(500):
        sts = []
        ok = True
        for i in range(nh):
            hi = float(rng.integers(130, 240))
            lo = float(rng.integers(40, 100))
            if hi - lo < 30:
                ok = False
                break
            sts.append(Stream("H" + str(i + 1), hi, lo, float(rng.integers(1, 9))))
        if not ok:
            continue
        for j in range(nc):
            lo = float(rng.integers(20, 90))
            hi = float(rng.integers(110, 200))
            if hi - lo < 30:
                ok = False
                break
            sts.append(Stream("C" + str(j + 1), lo, hi, float(rng.integers(1, 9))))
        if ok:
            return sts
    return None


def features(sts, dt, qmin):
    """Stream-level facts a bound could legitimately depend on."""
    pt = problem_table(sts, dt)
    hot_above = cold_above = hot_below = cold_below = 0
    pinch = pt["pinch_shifted_T"]
    for s in sts:
        a, b = s.shifted(dt)
        hi, lo = max(a, b), min(a, b)
        above = pinch is not None and hi > pinch
        below = pinch is not None and lo < pinch
        if s.hot:
            hot_above += 1 if above else 0
            hot_below += 1 if below else 0
        else:
            cold_above += 1 if above else 0
            cold_below += 1 if below else 0
    return {"hot": len([s for s in sts if s.hot]), "cold": len([s for s in sts if not s.hot]),
            "hot_above_pinch": hot_above, "cold_above_pinch": cold_above,
            "hot_below_pinch": hot_below, "cold_below_pinch": cold_below,
            "Q_H_min_positive": bool(qmin > 1e-9)}


TRAIN_SHAPES = [(2, 2), (2, 2), (2, 3), (3, 2), (2, 2), (3, 2), (2, 3), (3, 3)]
train, test = [], []
seen = set()
for shp in TRAIN_SHAPES:
    for _ in range(40):
        sts = draw(*shp)
        if sts is None:
            continue
        key = tuple(sorted((s.t_in, s.t_out, s.cp) for s in sts))
        if key in seen:
            continue
        dt = float(rng.choice([5, 10, 15]))
        try:
            qmin, u = minimum_units_attaining(sts, dt)
        except Exception:
            continue
        seen.add(key)
        rec = {"dt_min": dt, "Q_H_min": qmin, "min_units": u,
               "streams": [{"name": s.name, "t_in": s.t_in, "t_out": s.t_out, "cp": s.cp}
                           for s in sts]}
        rec.update(features(sts, dt, qmin))
        train.append(rec)
        break

for _ in range(60):
    sts = draw(2, 3)
    if sts is None:
        continue
    key = tuple(sorted((s.t_in, s.t_out, s.cp) for s in sts))
    if key in seen:
        continue
    dt = float(rng.choice([5, 10, 15]))
    qmin, u = minimum_units_attaining(sts, dt)
    seen.add(key)
    rec = {"dt_min": dt, "Q_H_min": qmin, "min_units": u,
           "streams": [{"name": s.name, "t_in": s.t_in, "t_out": s.t_out, "cp": s.cp}
                       for s in sts]}
    rec.update(features(sts, dt, qmin))
    test.append(rec)
    break

print("=" * 104)
print("TRAINING OBSERVATIONS (the agent sees all of this, including min_units)")
print("=" * 104)
print("  " + "case".rjust(5) + "nh".rjust(4) + "nc".rjust(4) + "dt".rjust(5)
      + "N(with HU)".rjust(11) + "N-1".rjust(5) + "hot>p".rjust(7) + "cold>p".rjust(8)
      + "hot<p".rjust(7) + "cold<p".rjust(8) + "min_units".rjust(11) + "  N-1 true?".rjust(11))
for i, r in enumerate(train):
    N = r["hot"] + r["cold"] + (1 if r["Q_H_min_positive"] else 0)
    print("  " + ("T" + str(i + 1)).rjust(5) + str(r["hot"]).rjust(4) + str(r["cold"]).rjust(4)
          + format(r["dt_min"], ".0f").rjust(5) + str(N).rjust(11) + str(N - 1).rjust(5)
          + str(r["hot_above_pinch"]).rjust(7) + str(r["cold_above_pinch"]).rjust(8)
          + str(r["hot_below_pinch"]).rjust(7) + str(r["cold_below_pinch"]).rjust(8)
          + str(r["min_units"]).rjust(11)
          + ("   yes" if r["min_units"] == N - 1 else "   NO").rjust(11))

print()
print("=" * 104)
print("HELD-OUT CASE (the agent is given the stream data and NOT the answer)")
print("=" * 104)
t = test[0]
N = t["hot"] + t["cold"] + (1 if t["Q_H_min_positive"] else 0)
print("  " + "nh".rjust(4) + "nc".rjust(4) + "dt".rjust(5) + "N(with HU)".rjust(11)
      + "N-1".rjust(5) + "hot>p".rjust(7) + "cold>p".rjust(8) + "hot<p".rjust(7)
      + "cold<p".rjust(8) + "   TRUE min_units (withheld from the agent)".rjust(42))
print("  " + str(t["hot"]).rjust(4) + str(t["cold"]).rjust(4) + format(t["dt_min"], ".0f").rjust(5)
      + str(N).rjust(11) + str(N - 1).rjust(5) + str(t["hot_above_pinch"]).rjust(7)
      + str(t["cold_above_pinch"]).rjust(8) + str(t["hot_below_pinch"]).rjust(7)
      + str(t["cold_below_pinch"]).rjust(8) + str(t["min_units"]).rjust(42))

print()
print("  how often does the textbook U >= N - 1 hold on the training set? "
      + str(sum(1 for r in train
                if r["min_units"] == r["hot"] + r["cold"]
                + (1 if r["Q_H_min_positive"] else 0) - 1)) + " of " + str(len(train)))

path = pathlib.Path(__file__).resolve().parents[1] / "runs" / "units_bound.json"
path.parent.mkdir(exist_ok=True)
path.write_text(json.dumps({"train": train, "test": test}, indent=1), encoding="utf-8")
print()
print("wrote runs/units_bound.json")
