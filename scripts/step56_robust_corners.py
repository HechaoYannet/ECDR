"""Step 56 - the corrected robustness test, and the corrected threshold.

Step 55 found that robust_violation's 12 random draws understate the worst case, and that
the true worst point is the (+, +) CORNER of the +-10 percent box: wn = 121.56111, zeta =
0.65506 against a nominal of (110.51010, 0.59551), i.e. exactly nominal times 1.1 in both
coordinates.

That makes the fix concrete and cheap.  A relative box has 2^d corners - four for two
parameters - and the constraints involved are monotone in the parameters, so the corners
are where the extremes live.  Random sampling of a box is the wrong instrument; the corners
are not a heuristic, they are the candidate set.

This recomputes the threshold with corners included and reports how far the false-positive
zone of Finding 008 moves.
"""
import _bootstrap  # noqa: F401
import itertools
import json
import pathlib

import numpy as np
from scipy.optimize import brentq

from ecdr.l0 import G, IsolationTask, PassiveSDOF, certify_passive_sdof
from ecdr.l0.feasibility import SEARCH_OMEGA
from ecdr.l1 import robust_violation

line = "=" * 92
m1 = PassiveSDOF()


def violation_at(p, task):
    T = np.abs(m1.transmissibility(SEARCH_OMEGA, p))
    band = SEARCH_OMEGA >= task.omega_low
    return max(float(T[band].max() / task.T_iso - 1.0),
               float(T.max() / task.A_max - 1.0),
               float(m1.static_deflection(p) / task.delta_max - 1.0))


def corner_violation(p, task, rel):
    """Worst violation over the 2^d corners of the perturbation box."""
    p = np.asarray(p, dtype=float)
    lo = np.array([b[0] for b in m1.param_bounds], dtype=float)
    hi = np.array([b[1] for b in m1.param_bounds], dtype=float)
    best = -np.inf
    arg = None
    for signs in itertools.product((-1.0, 1.0), repeat=p.size):
        q = np.clip(p * (1.0 + rel * np.asarray(signs)), lo, hi)
        v = violation_at(q, task)
        if v > best:
            best, arg = v, q
    return float(best), arg


def l0_feasible(task, p):
    T = np.abs(m1.transmissibility(SEARCH_OMEGA, p))
    band = SEARCH_OMEGA >= task.omega_low
    return (T[band].max() <= task.T_iso and T.max() <= task.A_max
            and m1.static_deflection(p) <= task.delta_max)


def robust_feasible(task, rel, use_corners):
    wn_min = float(np.sqrt(G / task.delta_max))
    for wn in np.linspace(wn_min, 3.0 * wn_min, 70):
        for z in np.concatenate([np.linspace(0.35, 1.5, 90), np.linspace(1.55, 3.5, 40)]):
            p = (wn, float(z))
            if not l0_feasible(task, p):
                continue
            if use_corners:
                v, _ = corner_violation(p, task, rel)
                if v <= 0.0:
                    return True, p
            else:
                if robust_violation(m1, p, task, SEARCH_OMEGA,
                                    rel=rel, n=12, seed=3) <= 0.0:
                    return True, p
    return False, None


print(line)
print("A. corners against the 12-draw sample, on the designs step 15 accepted")
print(line)
print("  " + "f_low".rjust(8) + "sampled n=12".rjust(14) + "corners".rjust(14)
      + "difference".rjust(13) + "  design".rjust(22))
rows = []
for f in (250.0, 270.0, 300.0):
    task = IsolationTask("probe", f, -20.0, 3.0, 1.0e-3)
    ok, p = robust_feasible(task, 0.10, use_corners=False)
    if not ok:
        continue
    s = robust_violation(m1, p, task, SEARCH_OMEGA, rel=0.10, n=12, seed=3)
    c, at = corner_violation(p, task, 0.10)
    rows.append({"f_low": f, "sampled": s, "corners": c,
                 "at": [float(at[0]), float(at[1])], "nominal": [float(p[0]), float(p[1])]})
    print("  " + format(f, ".0f").rjust(8) + format(s, ".5e").rjust(14)
          + format(c, ".5e").rjust(14) + format(c - s, ".5e").rjust(13)
          + ("(" + format(p[0], ".2f") + ", " + format(p[1], ".3f") + ")").rjust(22))
print()
for r in rows:
    print("  f_low " + format(r["f_low"], ".0f") + ": worst corner at wn = "
          + format(r["at"][0], ".5f") + ", zeta = " + format(r["at"][1], ".5f")
          + "   (nominal " + format(r["nominal"][0], ".5f") + ", "
          + format(r["nominal"][1], ".5f") + ")")

print()
print(line)
print("B. the corrected threshold")
print(line)
print("  " + "requirement".ljust(26) + "threshold Hz".rjust(15) + "  note".rjust(30))
res = {}
for rel, tag in ((0.0, "L0 (no perturbation)"), (0.10, "L1 +-10 percent, corners")):
    def ok(f):
        task = IsolationTask("probe", f, -20.0, 3.0, 1.0e-3)
        if rel == 0.0:
            return certify_passive_sdof(task).feasible
        return robust_feasible(task, rel, use_corners=True)[0]
    lo, hi = 150.0, 900.0
    if ok(hi):
        thr = brentq(lambda f: (1.0 if ok(f) else 0.0) - 0.5, lo, hi, xtol=0.5)
        res[tag] = thr
        print("  " + tag.ljust(26) + format(thr, "15.2f"))
    else:
        res[tag] = None
        print("  " + tag.ljust(26) + "         > 900")
res["L1 +-10 percent, 12 draws (step 15)"] = 239.72
print("  " + "L1 +-10 percent, 12 draws".ljust(26) + format(239.72, "15.2f")
      + "  as originally reported".rjust(30))

print()
print(line)
print("C. the corrected false-positive zone")
print(line)
l0t = res.get("L0 (no perturbation)")
l1t = res.get("L1 +-10 percent, corners")
if l0t and l1t:
    print("  L0 certificate threshold        : " + format(l0t, ".2f") + " Hz")
    print("  L1 robustness threshold, corners: " + format(l1t, ".2f") + " Hz")
    print("  L1 robustness threshold, 12 draws: 239.72 Hz  (understated)")
    print()
    print("  false-positive zone as originally reported : 172.34 to 239.72 Hz")
    print("  false-positive zone corrected              : " + format(l0t, ".2f")
          + " to " + format(l1t, ".2f") + " Hz")
    print("  width " + format(239.72 - 172.34, ".1f") + " Hz  ->  "
          + format(l1t - l0t, ".1f") + " Hz")

out = pathlib.Path(__file__).resolve().parents[1] / "runs"
out.mkdir(exist_ok=True)
(out / "robust_corners.json").write_text(json.dumps({
    "rows": rows, "thresholds": res,
}, indent=1), encoding="utf-8")
print()
print("wrote runs/robust_corners.json")
